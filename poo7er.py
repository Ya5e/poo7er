import argparse
import os
import random
import time
import platform
from zoneinfo import available_timezones
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.syntax import Syntax
from rich.tree import Tree
from rich.columns import Columns
from rich.text import Text
from playwright.async_api import async_playwright, BrowserContext
import signal
import sys
import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
import aiofiles
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Rich console
console = Console(width=180)  # Adjust this width as needed

# Dracula color scheme
DRACULA_COLORS = {
    "background": "#282a36",
    "current_line": "#44475a",
    "foreground": "#f8f8f2",
    "comment": "#6272a4",
    "cyan": "#8be9fd",
    "green": "#50fa7b",
    "orange": "#ffb86c",
    "pink": "#ff79c6",
    "purple": "#bd93f9",
    "red": "#ff5555",
    "yellow": "#f1fa8c"
}

# Twitch API credentials from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# List of games to retrieve clips for
games_list = ['Age of Empires II', 'Deadlock', 'Counter-Strike', 'Dota 2', 'Rust']

# Paths to files for user agents and proxies
USER_AGENTS_FILE = 'user_agents.txt'
PROXY_FILE = 'proxies.txt'

# Mobile viewport sizes
MOBILE_VIEWPORTS = [
    {"width": 360, "height": 640},  # Common Android phone
    {"width": 375, "height": 667},  # iPhone 6/7/8
    {"width": 414, "height": 896},  # iPhone XR/11
    {"width": 412, "height": 915},  # Pixel 5
]

# Increase the default timeout and add retry logic
DEFAULT_TIMEOUT = 0000  # 120 seconds
MAX_RETRIES = 3

# Load user agents and proxies
def load_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    return []

USER_AGENTS = load_from_file(USER_AGENTS_FILE)
PROXIES = load_from_file(PROXY_FILE)

def get_random_user_agent():
    return random.choice(USER_AGENTS) if USER_AGENTS else None

def get_random_proxy():
    return random.choice(PROXIES) if PROXIES else None

# Function to check if a file exists
def file_exists(filename):
    return os.path.isfile(filename)

# Graceful exit handler for CTRL+C
def signal_handler(sig, frame):
    console.print("🛑 Program terminated by user (CTRL+C). Exiting...", style=f"bold {DRACULA_COLORS['red']}")
    sys.exit(0)

# Attach the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Function to get OAuth token from Twitch
async def get_twitch_oauth_token(client_id, client_secret):
    if not client_id or not client_secret:
        raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in the .env file")
    
    url = 'https://id.twitch.tv/oauth2/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                token_data = await response.json()
                return token_data['access_token']
            else:
                error_content = await response.text()
                raise ValueError(f"Failed to get OAuth token. Status: {response.status}, Content: {error_content}")

# Function to get game ID from game name
async def get_game_id(game_name, oauth_token, client_id):
    url = 'https://api.twitch.tv/helix/games'
    headers = {
        'Client-Id': client_id,
        'Authorization': f'Bearer {oauth_token}'
    }
    params = {'name': game_name}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                games = data.get('data', [])
                return games[0]['id'] if games else None
            else:
                raise Exception(f"Failed to get game ID. Status: {response.status}")

# Function to get top clips for a specific game (filtered by clips no older than 4 weeks)
async def get_top_clips(game_name, oauth_token, client_id, limit=5):
    url = 'https://api.twitch.tv/helix/clips'
    headers = {
        'Client-Id': client_id,
        'Authorization': f'Bearer {oauth_token}'
    }

    four_weeks_ago = (datetime.utcnow() - timedelta(weeks=4)).isoformat("T") + "Z"

    game_id = await get_game_id(game_name, oauth_token, client_id)
    if not game_id:
        console.print(f"Game '{game_name}' not found.", style=f"bold {DRACULA_COLORS['red']}")
        return []

    params = {
        'game_id': game_id,
        'first': limit,
        'started_at': four_weeks_ago
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('data', [])
            else:
                raise Exception(f"Failed to get clips. Status: {response.status}")

# Define a dictionary mapping locales to likely timezones
LOCALE_TIMEZONE_MAP = {
    'en-US': [
        ('America/New_York', (40.7128, -74.0060)),
        ('America/Chicago', (41.8781, -87.6298)),
        ('America/Denver', (39.7392, -104.9903)),
        ('America/Los_Angeles', (34.0522, -118.2437))
    ],
    'en-GB': [('Europe/London', (51.5074, -0.1278))],
    'fr-FR': [('Europe/Paris', (48.8566, 2.3522))],
    'de-DE': [('Europe/Berlin', (52.5200, 13.4050))],
    'es-ES': [('Europe/Madrid', (40.4168, -3.7038))],
    # Add more as needed
}

async def create_browser_context(playwright, headless=True):
    user_agent = get_random_user_agent()
    
    # Choose a random locale
    locale = random.choice(list(LOCALE_TIMEZONE_MAP.keys()))
    
    # Choose a timezone and its approximate coordinates that match the locale
    timezone_id, (base_lat, base_lon) = random.choice(LOCALE_TIMEZONE_MAP[locale])
    
    # Add some randomness to the coordinates (within roughly 300km)
    latitude = base_lat + random.uniform(-3, 3)
    longitude = base_lon + random.uniform(-3, 3)
    
    # Get the current time in the chosen timezone
    current_time = datetime.now(ZoneInfo(timezone_id))
    
    context_options = {
        'viewport': random.choice(MOBILE_VIEWPORTS),
        'device_scale_factor': random.choice([1, 2]),
        'has_touch': True,
        'locale': locale,
        'timezone_id': timezone_id,
        'permissions': ['geolocation'],
        'geolocation': {
            'latitude': latitude,
            'longitude': longitude
        },
        'color_scheme': random.choice(['dark', 'light']),
        'bypass_csp': True,
        'ignore_https_errors': True,
        'java_script_enabled': True,
    }

    browser = await playwright.firefox.launch(headless=headless)
    context = await browser.new_context(**context_options)
    browser_info = f"Firefox {browser.version}"

    return browser, context, user_agent, PROXIES, context_options, browser_info

# Function to echo network information
async def echo_network_info(user_agent, proxies, context_options, browser_info):
    ip_address = await get_ip_address()
    
    console.print(f"[{DRACULA_COLORS['orange']}]Network Information[/{DRACULA_COLORS['orange']}]")
    console.print(f"IP Address: [{DRACULA_COLORS['cyan']}]{ip_address}[/{DRACULA_COLORS['cyan']}]")
    console.print(f"Browser: [{DRACULA_COLORS['green']}]{browser_info} ({platform.system()} {platform.machine()})[/{DRACULA_COLORS['green']}]")
    console.print(f"User Agent: [{DRACULA_COLORS['foreground']}]{user_agent}[/{DRACULA_COLORS['foreground']}]")
    console.print(f"Proxies: [{DRACULA_COLORS['yellow']}]{len(proxies)} available[/{DRACULA_COLORS['yellow']}]")
    console.print()

    console.print(f"[{DRACULA_COLORS['orange']}]Context Options[/{DRACULA_COLORS['orange']}]")
    
    table = Table(show_header=False, show_lines=False, box=None, padding=(0, 2, 0, 0))
    table.add_column("Key", style=DRACULA_COLORS['cyan'])
    table.add_column("Value", style=DRACULA_COLORS['pink'])
    table.add_column("Description", style=DRACULA_COLORS['comment'])

    for key, value in context_options.items():
        if key == 'user_agent':
            continue  # Skip user_agent in context options
        
        if key == 'viewport':
            value_str = f"{value['width']}x{value['height']}"
        elif key == 'permissions':
            value_str = ', '.join(value)
        elif key == 'geolocation':
            value_str = f"Lat: {value['latitude']}, Lon: {value['longitude']}"
        elif isinstance(value, bool):
            value_str = f"[{DRACULA_COLORS['green']}]{value}[/{DRACULA_COLORS['green']}]"
        else:
            value_str = str(value)

        description = get_description(key)
        table.add_row(key, value_str, description)

    console.print(table)

def get_description(key):
    descriptions = {
        'viewport': '(Browser window size)',
        'device_scale_factor': '(Display density)',
        'has_touch': '(Supports touch events)',
        'locale': '(Browser language)',
        'timezone_id': '(Simulated timezone)',
        'permissions': '(Granted permissions)',
        'geolocation': '(Simulated location)',
        'color_scheme': '(Preferred color scheme)',
        'bypass_csp': '(Bypass Content Security Policy)',
        'ignore_https_errors': '(Ignore HTTPS errors)',
        'java_script_enabled': '(JavaScript execution)'
    }
    return descriptions.get(key, '')

# Function to get IP address
async def get_ip_address():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.ipify.org') as response:
            return await response.text()

# Function to get video URL from clip page
async def get_video_url(page, clip_url, proxies):
    console.print(f"Navigating to clip URL: {clip_url}", style=DRACULA_COLORS['yellow'])
    start_time = time.time()
    
    try:
        # Navigate to the page without waiting for load events
        await page.goto(clip_url, wait_until='domcontentloaded', timeout=DEFAULT_TIMEOUT)
        console.print(f"Initial page load completed in {time.time() - start_time:.2f} seconds", style=DRACULA_COLORS['cyan'])
    except Exception as e:
        console.print(f"Error during page navigation: {str(e)}", style=DRACULA_COLORS['red'])
        return None

    async def mute_video(show_notification=False):
        num_videos_muted = await page.evaluate("""
            () => {
                const videos = document.querySelectorAll('video');
                videos.forEach(video => {
                    video.muted = true;
                    video.volume = 0;
                });
                return videos.length;  // Return the number of videos muted
            }
        """)
        if show_notification:
            console.print(f"🔇 Muted {num_videos_muted} video(s)", style=DRACULA_COLORS['cyan'])

    # Initial mute with notification
    await mute_video(show_notification=True)

    console.print("Searching for video element...", style=DRACULA_COLORS['yellow'])
    video_url = None
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            # Mute video before each attempt (without notification)
            await mute_video()
            
            # Simulate user interaction
            x, y = random.randint(0, 500), random.randint(0, 500)
            console.print(f"🖱️ Simulating user interaction: Mouse move to ({x}, {y}) and click", style=DRACULA_COLORS['cyan'])
            await page.mouse.move(x=x, y=y)
            await page.mouse.down()
            await page.mouse.up()

            # Check for video element
            video_url = await page.evaluate('''() => {
                const videoElement = document.querySelector('video[src]');
                return videoElement ? videoElement.src : null;
            }''')
            
            if video_url:
                console.print(f"Video URL found on attempt {attempt + 1}", style=DRACULA_COLORS['green'])
                break
        except Exception as e:
            console.print(f"Attempt {attempt + 1} failed: {str(e)}", style=DRACULA_COLORS['red'])

        # Wait a short time before the next attempt
        await asyncio.sleep(1)

    # Final mute without notification
    await mute_video()

    if video_url:
        console.print(f"Signed URL Extracted in {time.time() - start_time:.2f} seconds: {video_url}", style=DRACULA_COLORS['green'])
        return video_url
    else:
        console.print(f"Failed to extract video URL after {max_attempts} attempts", style=DRACULA_COLORS['red'])
        return None
    

async def download_clip(page, session, clip, proxies):
    filename = f"{clip['title'].replace(' ', '_')}.mp4"
    if file_exists(filename):
        console.print(f"Clip '{clip['title']}' already exists. Skipping download.", style=DRACULA_COLORS['yellow'])
        return

    console.print(f"Attempting to download clip: {clip['title']}", style=DRACULA_COLORS['cyan'])
    
    for attempt in range(MAX_RETRIES):
        try:
            start_time = time.time()
            video_url = await get_video_url(page, clip['url'], proxies)
            if not video_url:
                raise Exception("Failed to get video URL")

            async with session.get(video_url) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))

                with Progress() as progress:
                    download_task = progress.add_task("[cyan]Downloading...", total=total_size)
                    async with aiofiles.open(filename, 'wb') as file:
                        async for chunk in response.content.iter_chunked(1024):
                            await file.write(chunk)
                            progress.update(download_task, advance=len(chunk))

            end_time = time.time()
            download_time = end_time - start_time
            file_size = os.path.getsize(filename)
            
            console.print(f"✅ Clip downloaded successfully: {filename}", style=DRACULA_COLORS['green'])
            console.print(f"File size: {file_size / (1024 * 1024):.2f} MB", style=DRACULA_COLORS['yellow'])
            console.print(f"Download time: {download_time:.2f} seconds", style=DRACULA_COLORS['yellow'])
            return
        except Exception as e:
            console.print(f"Attempt {attempt + 1} failed: {str(e)}", style=DRACULA_COLORS['red'])
            if attempt < MAX_RETRIES - 1:
                console.print(f"Retrying in 5 seconds...", style=DRACULA_COLORS['yellow'])
                await asyncio.sleep(5)
            else:
                console.print(f"❌ Failed to download clip after {MAX_RETRIES} attempts", style=DRACULA_COLORS['red'])

# Function to list top clips
async def list_clips(limit, oauth_token, client_id, game=None, headless=True):
    async with async_playwright() as p:
        browser, context, user_agent, proxies, context_options, browser_version = await create_browser_context(p, headless)
        await echo_network_info(user_agent, proxies, context_options, browser_version)
        
        games_to_process = [game] if game else games_list
        for game in games_to_process:
            console.print(f"\nFetching top {limit} clips for game '{game}'", style=f"bold {DRACULA_COLORS['cyan']}")
            try:
                clips = await get_top_clips(game, oauth_token, client_id, limit=limit)
                if clips:
                    table = Table(title=f"Top {len(clips)} Clips for {game}", style=DRACULA_COLORS['purple'])
                    table.add_column("Title", style=DRACULA_COLORS['green'])
                    table.add_column("Broadcaster", style=DRACULA_COLORS['orange'])
                    table.add_column("Creator", style=DRACULA_COLORS['yellow'])
                    table.add_column("Views", style=DRACULA_COLORS['pink'], justify="right")
                    table.add_column("URL", style=DRACULA_COLORS['cyan'])
                    table.add_column("Language", style=DRACULA_COLORS['foreground'])
                    table.add_column("Created At", style=DRACULA_COLORS['foreground'])
                    table.add_column("Status", style=DRACULA_COLORS['purple'])

                    for clip in clips:
                        filename = f"{clip['title'].replace(' ', '_')}.mp4"
                        status = "📥 Downloaded" if file_exists(filename) else "🆕 New"
                        table.add_row(
                            clip['title'],
                            clip['broadcaster_name'],
                            clip['creator_name'],
                            str(clip['view_count']),
                            clip['url'],
                            clip['language'],
                            clip['created_at'],
                            status
                        )

                    console.print(table)
                else:
                    console.print(f"No clips found for '{game}'", style=DRACULA_COLORS['yellow'])
            except Exception as e:
                console.print(f"❌ Error fetching clips for '{game}': {str(e)}", style=f"bold {DRACULA_COLORS['red']}")
        
        await browser.close()

# Function to download latest clips
async def download_latest_clips(limit, oauth_token, client_id, game=None, headless=True):
    async with async_playwright() as p:
        browser, context, user_agent, proxies, context_options, browser_version = await create_browser_context(p, headless)
        await echo_network_info(user_agent, proxies, context_options, browser_version)
        page = await context.new_page()
        
        try:
            async with aiohttp.ClientSession() as session:
                games_to_process = [game] if game else games_list
                for game in games_to_process:
                    console.print(f"\nFetching top {limit} clips for game '{game}'", style=f"bold {DRACULA_COLORS['cyan']}")
                    clips = await get_top_clips(game, oauth_token, client_id, limit=limit)
                    if clips:
                        for clip in clips:
                            await download_clip(page, session, clip, proxies)
                    else:
                        console.print(f"No clips found for '{game}'", style=DRACULA_COLORS['yellow'])
        finally:
            await browser.close()

# Function to test download one clip
async def test_download_one_clip(limit, oauth_token, client_id, game=None, headless=True):
    async with async_playwright() as p:
        browser, context, user_agent, proxies, context_options, browser_version = await create_browser_context(p, headless)
        await echo_network_info(user_agent, proxies, context_options, browser_version)
        page = await context.new_page()
        
        game = game or random.choice(games_list)
        console.print(f"\nTesting download for game '{game}'", style=f"bold {DRACULA_COLORS['cyan']}")

        try:
            clips = await get_top_clips(game, oauth_token, client_id, limit=limit)
            if clips:
                clip = random.choice(clips)  # Randomly select one clip
                clip_info = Tree("Clip Information", style=DRACULA_COLORS['purple'])
                clip_info.add(f"Clip URL: {clip['url']}", style=DRACULA_COLORS['cyan'])
                clip_info.add(f"Clip Title: {clip['title']}", style=DRACULA_COLORS['green'])
                clip_info.add(f"Broadcaster: {clip['broadcaster_name']}", style=DRACULA_COLORS['orange'])
                clip_info.add(f"Creator: {clip['creator_name']}", style=DRACULA_COLORS['yellow'])
                clip_info.add(f"Created At: {clip['created_at']}", style=DRACULA_COLORS['pink'])
                console.print(clip_info)
                
                async with aiohttp.ClientSession() as session:
                    await download_clip(page, session, clip, proxies)
            else:
                console.print(f"❌ No clips found for '{game}'", style=f"bold {DRACULA_COLORS['red']}")
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style=f"bold {DRACULA_COLORS['red']}")
        
        await browser.close()

# Function to download a specific clip by title
async def download_clip_by_title(title, oauth_token, client_id, game=None, headless=True):
    async with async_playwright() as p:
        browser, context, user_agent, proxies, context_options, browser_version = await create_browser_context(p, headless)
        await echo_network_info(user_agent, proxies, context_options, browser_version)
        page = await context.new_page()
        
        async with aiohttp.ClientSession() as session:
            games_to_search = [game] if game else games_list
            for game in games_to_search:
                console.print(f"\nSearching for clip '{title}' in game '{game}'", style=f"bold {DRACULA_COLORS['cyan']}")
                clips = await get_top_clips(game, oauth_token, client_id, limit=100)  # Increase limit to search more clips
                matching_clip = next((clip for clip in clips if clip['title'].lower() == title.lower()), None)
                if matching_clip:
                    await download_clip(page, session, matching_clip, proxies)
                    break
            else:
                console.print(f"❌ Clip '{title}' not found in any game", style=f"bold {DRACULA_COLORS['red']}")
        
        await browser.close()

# Function to list supported games
def list_supported_games(): 
    console.print("Supported Games:", style=f"bold {DRACULA_COLORS['cyan']}")
    for game in games_list:
        console.print(f"- {game}", style=DRACULA_COLORS['green'])

# Welcome screen using Rich
def print_welcome_screen():
    logo = Text(r"""
██████╗░░█████╗░░█████╗░███████╗███████╗██████╗░
██╔══██╗██╔══██╗██╔══██╗╚════██║██╔════╝██╔══██╗
██████╔╝██║░░██║██║░░██║░░░░██╔╝█████╗░░██████╔╝
██╔═══╝░██║░░██║██║░░██║░░░██╔╝░██╔══╝░░██╔══██╗
██║░░░░░╚█████╔╝╚█████╔╝░░██╔╝░░███████╗██║░░██║
╚═╝░░░░░░╚════╝░░╚════╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝
""", style=f"bold {DRACULA_COLORS['purple']}")

    console.print(logo)
    console.print("\nWelcome to POO7ER - I put the POOT in your sources! Gimmie those thicc trendy clips and I'll suck'em down. I drink the bytes of signed-urls!", style=f"bold {DRACULA_COLORS['green']}")
    console.print("\nAvailable Commands:", style=f"bold {DRACULA_COLORS['cyan']}")
    
    commands = [
        ("-dl, --download-latest", "Download the latest top clips. Can be combined with `-g` to specify a game and `-l` to set a clip limit."),
        ("-dt, --download-title ", "Download a specific clip by title. Requires the `-g` flag to specify the game the clip is from."),
        ("-g,  --game <game>    ", "Specify a game to filter clips for use with `-lc`, `-dl`, `-td`, or `-dt`. Must be combined with these commands."),
        ("-gs, --games-supported", "List all games supported by the tool without performing any downloads."),
        ("-h,  --help           ", "Show this help message and exit."),
        ("-l,  --limit <number> ", "Limit the number of clips for use with `-lc` (list clips), `-dl` (download latest clips), or `-td` (test download). Defaults to 5 if not provided."),
        ("-lc, --list-clips     ", "List the top clips for a specified game. Can be combined with `-g` and `-l` for filtering."),
        ("-sb, --show-browser   ", "Show the browser during the clip download process for troubleshooting purposes."),
        ("-td, --test-download  ", "Test downloading a random clip from a specific game. Requires `-g` to specify the game and can use `-l` to limit the number of clips checked.")
    ]

    for command, description in commands:
        console.print(f"[{DRACULA_COLORS['pink']}]{command:<30}[/{DRACULA_COLORS['pink']}] {description}", 
                      style=DRACULA_COLORS['foreground'])

# Main CLI app function
async def main():
    parser = argparse.ArgumentParser(description="POO7ER: Twitch Clip CLI Tool")
    parser.add_argument('-gs', '--games-supported', action='store_true', help='List all supported games')
    parser.add_argument('-g', '--game', help='Specify a game')
    parser.add_argument('-lc', '--list-clips', action='store_true', help='List top clips')
    parser.add_argument('-dl', '--download-latest', action='store_true', help='Download top clips')
    parser.add_argument('-td', '--test-download', action='store_true', help='Test download one clip')
    parser.add_argument('-l', '--limit', type=int, help='Limit number of clips', default=5)
    parser.add_argument('-dt', '--download-title', help='Download a specific clip by title')
    parser.add_argument('-sb', '--show-browser', action='store_true', help='Show browser for troubleshooting')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        print_welcome_screen()
        return

    # Check if only -g or -l are used without appropriate accompanying switches
    if (args.game is not None or args.limit != 5) and not (args.list_clips or args.download_latest or args.test_download or args.download_title or args.games_supported):
        console.print("Error: -g (--game) and -l (--limit) should be used with -lc, -dl, -td, or -dt.", style=f"bold {DRACULA_COLORS['red']}")
        console.print("For example:", style=DRACULA_COLORS['yellow'])
        console.print("  python poo7er.py -lc -g Rust -l 10", style=DRACULA_COLORS['yellow'])
        console.print("  python poo7er.py -dl -g 'Counter-Strike' -l 5", style=DRACULA_COLORS['yellow'])
        console.print("  python poo7er.py -td -g Dota2", style=DRACULA_COLORS['yellow'])
        console.print("  python poo7er.py -dt 'Amazing play' -g Rust", style=DRACULA_COLORS['yellow'])
        return

    try:
        oauth_token = await get_twitch_oauth_token(CLIENT_ID, CLIENT_SECRET)

        if args.games_supported:
            list_supported_games()
        elif args.list_clips:
            await list_clips(args.limit, oauth_token, CLIENT_ID, args.game, headless=not args.show_browser)
        elif args.download_latest:
            await download_latest_clips(args.limit, oauth_token, CLIENT_ID, args.game, headless=not args.show_browser)
        elif args.test_download:
            await test_download_one_clip(args.limit, oauth_token, CLIENT_ID, args.game, headless=not args.show_browser)
        elif args.download_title:
            await download_clip_by_title(args.download_title, oauth_token, CLIENT_ID, args.game, headless=not args.show_browser)
        else:
            parser.print_help()
    except ValueError as e:
        console.print(f"Error: {str(e)}", style=f"bold {DRACULA_COLORS['red']}")
        console.print("Please make sure you have set up your .env file with valid CLIENT_ID and CLIENT_SECRET.", style=DRACULA_COLORS['yellow'])
    except Exception as e:
        console.print(f"An unexpected error occurred: {str(e)}", style=f"bold {DRACULA_COLORS['red']}")
        console.print(f"Stack trace:", style=f"bold {DRACULA_COLORS['red']}")
        import traceback
        console.print(traceback.format_exc(), style=DRACULA_COLORS['red'])

if __name__ == '__main__':
    asyncio.run(main())



    
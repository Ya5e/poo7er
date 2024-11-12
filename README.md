# Poo7er

**Poo7er** is a Python-based application designed to download trending clips from Twitch, bypassing bot detection and DRM restrictions. It leverages Playwright for browser automation, allowing it to interact with Twitch dynamically while maintaining stealth to avoid detection.

---

```

██████╗░░█████╗░░█████╗░███████╗███████╗██████╗░
██╔══██╗██╔══██╗██╔══██╗╚════██║██╔════╝██╔══██╗
██████╔╝██║░░██║██║░░██║░░░░██╔╝█████╗░░██████╔╝
██╔═══╝░██║░░██║██║░░██║░░░██╔╝░██╔══╝░░██╔══██╗
██║░░░░░╚█████╔╝╚█████╔╝░░██╔╝░░███████╗██║░░██║
╚═╝░░░░░░╚════╝░░╚════╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝


Welcome to POO7ER - I put the POOT in your sources! Gimmie those thicc trendy clips and I'll suck'em down. I drink the bytes of signed-urls!

Available Commands:
-dl, --download-latest         Download the latest top clips. Can be combined with `-g` to specify a game and `-l` to set a clip limit.
-dt, --download-title          Download a specific clip by title. Requires the `-g` flag to specify the game the clip is from.
-g,  --game <game>             Specify a game to filter clips for use with `-lc`, `-dl`, `-td`, or `-dt`. Must be combined with these commands.
-gs, --games-supported         List all games supported by the tool without performing any downloads.
-h,  --help                    Show this help message and exit.
-l,  --limit <number>          Limit the number of clips for use with `-lc` (list clips), `-dl` (download latest clips), or `-td` (test download). Defaults to 5 if not provided.
-lc, --list-clips              List the top clips for a specified game. Can be combined with `-g` and `-l` for filtering.
-sb, --show-browser            Show the browser during the clip download process for troubleshooting purposes.
-td, --test-download           Test downloading a random clip from a specific game. Requires `-g` to specify the game and can use `-l` to limit the number of clips checked.
```

## Features

- **Trending Clip Downloads**: Automatically fetches and downloads popular clips from Twitch.
- **Bot Detection Bypass**: Uses Playwright to simulate human interactions, bypassing bot detection.
- **DRM Handling**: Designed to work around DRM restrictions for seamless clip downloading.
- **Customizable Parameters**: Supports various command-line options for targeted clip fetching and filtering.
- **Proxy Support**: Supports proxies, please add proxies to proxies.txt.rename and ensure proxies.txt is the filename.
- **Randomized User-Agent Rotation**: Rotates user-agents only uses MOBILE user-agents.

## Prerequisites

- **Docker**: Ensure Docker is installed on your machine.
- **Python**: Required if running outside Docker (Python 3.10+ recommended).

## Getting Started

To use **Poo7er** in a Docker environment, follow these steps:

### Build Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Ya5e/poo7er.git
   cd poo7er

2. **Configure Environment Variables**

   ```bash
   mv .env.example .env (edit with your keys)

3. **Build the Docker Image**

   ```bash
   docker build -t poo7er .

4. **Run the Container**

   ```bash
   docker run -it poo7er

5. **Example Commands**

    #### List all clips for the game Deadlock and limit the output to 10 clips.

   ```bash
   docker run -it poo7er -lc -g "Deadlock" -l=10
   ```

    ```
    Network Information
    IP Address: 100.100.100.100
    Browser: Firefox 130.0 (Linux x86_64)
    User Agent: Mozilla/5.0 (Android 12; Mobile; SM-S908E; rv:108.0) Gecko/108.0 Firefox/108.0
    Proxies: 0 available

    Context Options
    viewport             360x640                                           (Browser window size)
    device_scale_factor  2                                                 (Display density)
    has_touch            True                                              (Supports touch events)
    locale               es-ES                                             (Browser language)
    timezone_id          Europe/Madrid                                     (Simulated timezone)
    permissions          geolocation                                       (Granted permissions)
    geolocation          Lat: 39.11589511769584, Lon: -2.9677593614049345  (Simulated location)
    color_scheme         light                                             (Preferred color scheme)
    bypass_csp           True                                              (Bypass Content Security Policy)  
    ignore_https_errors  True                                              (Ignore HTTPS errors)
    java_script_enabled  True                                              (JavaScript execution)

    Fetching top 10 clips for game 'Deadlock'
                                                                                Top 10 Clips for Deadlock
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
    ┃ Title                                          ┃ Broadcaster  ┃ Creator      ┃ Views ┃ URL                                            ┃ Language ┃ Created At           ┃ Status ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
    │ RANDY COMMUNICATION                            │ FyroGaming   │ FyroGaming   │  5567 │ https://clips.twitch.tv/SparklingAbstemiousCh… │ de       │ 2024-10-18T21:28:02Z │ 🆕 New │
    │ ИГРАЕМ РАНКЕД В ШЕДЕВРЕ ОТ VALVE // Ковры в    │ Recrent      │ tekkyume     │  5515 │ https://clips.twitch.tv/SarcasticBlueNighting… │ ru       │ 2024-10-19T13:57:21Z │ 🆕 New │
    │ наличии !мерч !tg !pari                        │              │              │       │                                                │          │                      │        │
    │ выиграл с умалишенным                          │ sadnavaro    │ sadnavaro    │  3511 │ https://clips.twitch.tv/CourageousSparklyVani… │ ru       │ 2024-10-18T21:31:23Z │ 🆕 New │
    │ LYSTIC_ SOSAL GUBAMI                           │ jamside      │ diesfromdice │  2949 │ https://clips.twitch.tv/SuaveBadToothRitzMitz… │ ru       │ 2024-10-17T15:53:43Z │ 🆕 New │
    │ pixeldrocher                                   │ coldplushtoy │ coldplushtoy │  2309 │ https://clips.twitch.tv/AcceptableSpotlessLor… │ ru       │ 2024-10-16T13:58:36Z │ 🆕 New │
    │ anti aircraft goo                              │ vegas        │ naechosa     │  2111 │ https://clips.twitch.tv/PlausibleSparklyMuleD… │ en       │ 2024-10-15T22:13:12Z │ 🆕 New │
    │ ow issues                                      │ pkmk         │ pkmk         │  1969 │ https://clips.twitch.tv/SpotlessDependableCur… │ ru       │ 2024-10-17T11:56:41Z │ 🆕 New │
    │ Nice aimbot                                    │ A_Seagull    │ ASAP_Smash1  │  1697 │ https://clips.twitch.tv/PatientAggressivePizz… │ en       │ 2024-10-20T20:39:02Z │ 🆕 New │
    │ WHAT? x4                                       │ vegas        │ whysosunny   │  1637 │ https://clips.twitch.tv/HungryCuteUdonDancing… │ en       │ 2024-10-17T11:01:30Z │ 🆕 New │
    │ стиль                                          │ pkmk         │ pkmk         │  1609 │ https://clips.twitch.tv/EnergeticRoughPigeonH… │ ru       │ 2024-10-18T15:15:41Z │ 🆕 New │
    └────────────────────────────────────────────────┴──────────────┴──────────────┴───────┴────────────────────────────────────────────────┴──────────┴──────────────────────┴────────┘
    ```

    #### Download the latest trending clips for the game Deadlock and limit the output to 1 clip.

    ```bash
    docker run -it poo7er -dl -g "Deadlock" -l=1
    ```
    
    ```
    Network Information
    IP Address: 100.100.100.100
    Browser: Firefox 130.0 (Linux x86_64)
    User Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/40.0 Mobile/15E148 Safari/605.1.15
    Proxies: 0 available

    Context Options
    viewport             360x640                                            (Browser window size)
    device_scale_factor  2                                                  (Display density)
    has_touch            True                                               (Supports touch events)
    locale               es-ES                                              (Browser language)
    timezone_id          Europe/Madrid                                      (Simulated timezone)
    permissions          geolocation                                        (Granted permissions)
    geolocation          Lat: 39.226711099440124, Lon: -3.3050373174355485  (Simulated location)
    color_scheme         dark                                               (Preferred color scheme)
    bypass_csp           True                                               (Bypass Content Security Policy)  
    ignore_https_errors  True                                               (Ignore HTTPS errors)
    java_script_enabled  True                                               (JavaScript execution)

    Fetching top 1 clips for game 'Deadlock'
    Attempting to download clip: RANDY COMMUNICATION
    Navigating to clip URL: https://clips.twitch.tv/SparklingAbstemiousCheesecakeAMPEnergy--qSrOQNOLyyXQYFB
    Initial page load completed in 1.21 seconds
    🔇 Muted 0 video(s)
    Searching for video element...
    🖱️ Simulating user interaction: Mouse move to  (160, 99) and click
    🖱️ Simulating user interaction: Mouse move to  (485, 0) and click
    Video URL found on attempt 2
    Signed URL Extracted in 2.45 seconds: 
    https://production.assets.clips.twitchcdn.net/v2/media/SparklingAbstemiousCheesecakeAMPEnergy--qSrOQNOLyyXQYFB/b9e24e80-cbd6-4fe6-9e6c-0b385519d4f2/video.mp4?sig=045680af46470434b2
    ba33b7bd56771ddf75fd5c&token=%7B%22authorization%22%3A%7B%22forbidden%22%3Afalse%2C%22reason%22%3A%22%22%7D%2C%22clip_uri%22%3A%22%22%2C%22clip_slug%22%3A%22SparklingAbstemiousChee
    secakeAMPEnergy--qSrOQNOLyyXQYFB%22%2C%22device_id%22%3A%2278caeb4c59a804aa%22%2C%22expires%22%3A1731512762%2C%22user_id%22%3A%22%22%2C%22version%22%3A2%7D
    Downloading... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
    ✅ Clip downloaded successfully: RANDY_COMMUNICATION.mp4
    File size: 36.75 MB
    Download time: 6.66 seconds
    ```

## Development

If you’re working on Poo7er and want to run it locally (outside of Docker), ensure all dependencies are installed:

**Activate Environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Install Requirements**

```bash
pip install -r requirements.txt
```

**Run The Script**

```bash
python poo7er.py --game "League of Legends" --limit 5
```


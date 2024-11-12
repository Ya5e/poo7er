# Poo7er

**Poo7er** is a Python-based application designed to download trending clips from Twitch, bypassing bot detection and DRM restrictions. It leverages Playwright for browser automation, allowing it to interact with Twitch dynamically while maintaining stealth to avoid detection.

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

   ```bash
   docker run -it poo7er -lc -g "Deadlock" -l=10

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


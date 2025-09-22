import os
import sys
import json
import asyncio
import requests
import websockets
import ssl
import certifi
from dotenv import load_dotenv
from colorama import init, Fore, Style
from datetime import datetime, timedelta
from collections import deque

# ---------------- Init ---------------- #
init(autoreset=True)
load_dotenv()

log_buffer = deque(maxlen=15)  # keep last 15 logs
invalid_tokens = []  # rejected tokens

# ---------------- Helpers ---------------- #
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log_message(level, user, msg, color):
    entry = f"[{timestamp()}] {color}{level}{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}{user}{Style.RESET_ALL} → {msg}"
    log_buffer.append(entry)
    refresh_console()

def log_success(user, msg): log_message("[SUCCESS]", user, msg, Fore.GREEN)
def log_info(user, msg): log_message("[INFO]", user, msg, Fore.LIGHTMAGENTA_EX)
def log_error(user, msg): log_message("[ERROR]", user, msg, Fore.RED + Style.BRIGHT)

# ---------------- Banner ---------------- #
def print_banner(extra_info="Running..."):
    clear_console()
    ascii_logo = f"""
{Fore.LIGHTMAGENTA_EX}██████╗ ██╗███████╗ ██████╗ ██████╗  ██████╗ ██████╗ 
██╔══██╗██║██╔════╝██╔═══██╗██╔══██╗██╔═══██╗██╔══██╗
██████╔╝██║█████╗  ██║   ██║██████╔╝██║   ██║██████╔╝
██╔═══╝ ██║██╔══╝  ██║   ██║██╔═══╝ ██║   ██║██╔═══╝ 
██║     ██║███████╗╚██████╔╝██║  ██║╚██████╔╝██║     
╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     
{Style.RESET_ALL}
    """
    footer = f"""
{Fore.LIGHTMAGENTA_EX}═══════════════════════════════════════════════════════════════════════
 Made By:{Style.RESET_ALL} WILLIAM Holley
 {Fore.LIGHTMAGENTA_EX}Website:{Style.RESET_ALL} https://w4r.qzz.io
 {Fore.LIGHTMAGENTA_EX}Discord:{Style.RESET_ALL} https://w4r.qzz.io/discord
{Fore.LIGHTMAGENTA_EX}═══════════════════════════════════════════════════════════════════════
 Discord API:{Style.RESET_ALL} v10
 Discord Status:{Style.RESET_ALL} {get_discord_status()}
 Tokens Loaded:{Style.RESET_ALL} {len(tokens_usernames)} / {len(tokens_usernames) + len(invalid_tokens)} valid
───────────────────────────────────────────────────────────────────────
 [+] Success Logs
 [~] Info Logs
 [!] Error Logs
───────────────────────────────────────────────────────────────────────
 {extra_info}
{Fore.LIGHTMAGENTA_EX}═══════════════════════════════════════════════════════════════════════{Style.RESET_ALL}
    """
    print(ascii_logo)
    print(footer)

    # Show invalid tokens if any
    if invalid_tokens:
        print(f"{Fore.RED}[!] Rejected Tokens:{Style.RESET_ALL} {', '.join(invalid_tokens)}\n")

    for entry in log_buffer:
        print(entry)

def refresh_console():
    print_banner("Active session")

def print_stopping_banner():
    print_banner("Stopping software safely...")

# ---------------- Discord API Helpers ---------------- #
def get_discord_status():
    try:
        r = requests.get("https://discordstatus.com/api/v2/status.json", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("status", {}).get("description", "Unknown")
    except Exception:
        return "Status Unavailable"
    return "Status Unavailable"

def validate_token(token, username):
    try:
        headers = {"Authorization": token, "Content-Type": "application/json"}
        r = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
        if r.status_code == 200:
            return True
        else:
            invalid_tokens.append(username)
            return False
    except Exception:
        invalid_tokens.append(username)
        return False

# ---------------- Load Tokens ---------------- #
status_options = ["online", "idle", "dnd", "invisible"]
tokens_usernames = []
retry_delay = int(os.getenv("RETRY_DELAY", 15))
rotate_hours = int(os.getenv("ROTATE_HOURS", 0))
rotate_minutes = int(os.getenv("ROTATE_MINUTES", 0))

for i in range(1, 11):
    token = os.getenv(f"TOKEN{i}")
    username = os.getenv(f"USERNAME{i}", f"Token{i}")
    user_status = os.getenv(f"STATUS{i}", "online").lower()
    if user_status not in status_options:
        user_status = "online"
    if token and validate_token(token, username):
        tokens_usernames.append({
            "token": token,
            "username": username,
            "status": user_status,
            "next_rotate": None
        })

if not tokens_usernames:
    print(f"{Fore.RED}[!] No valid tokens found in .env. Exiting...{Style.RESET_ALL}")
    sys.exit()

# ---------------- Discord Gateway ---------------- #
ssl_context = ssl.create_default_context(cafile=certifi.where())
gateway_backups = [
    "wss://gateway.discord.gg",
    "wss://canary.gateway.discord.gg",
    "wss://ptb.gateway.discord.gg"
]

async def connect_ws(url):
    return await websockets.connect(
        url,
        max_size=None,
        ping_interval=None,
        open_timeout=10,
        close_timeout=10,
        ssl=ssl_context
    )

# ---------------- Worker ---------------- #
async def onliner(user):
    token, username, status = user["token"], user["username"], user["status"]

    while True:
        try:
            ws = None
            for gw in gateway_backups:
                try:
                    ws = await connect_ws(f"{gw}/?v=10&encoding=json")
                    break
                except Exception:
                    continue

            if not ws:
                log_error(username, "No gateway available. Retrying...")
                await asyncio.sleep(retry_delay)
                continue

            async with ws:
                start = json.loads(await ws.recv())
                heartbeat_interval = start["d"]["heartbeat_interval"] / 1000

                auth = {
                    "op": 2,
                    "d": {
                        "token": token,
                        "intents": 0,
                        "properties": {"$os": "linux", "$browser": "chrome", "$device": "pc"},
                        "presence": {"since": 0, "activities": [], "status": status, "afk": False}
                    },
                }
                await ws.send(json.dumps(auth))
                log_success(username, "Connected to gateway.")

                # schedule auto-rotate
                if rotate_hours or rotate_minutes:
                    rotate_delay = timedelta(hours=rotate_hours, minutes=rotate_minutes)
                    user["next_rotate"] = datetime.now() + rotate_delay

                while True:
                    await asyncio.sleep(heartbeat_interval)
                    await ws.send(json.dumps({"op": 1, "d": None}))

                    if user["next_rotate"] and datetime.now() >= user["next_rotate"]:
                        log_info(username, "Auto-rotating reconnect...")
                        await ws.close()
                        break

        except Exception as e:
            log_error(username, f"Exception: {e}")
            await asyncio.sleep(retry_delay)

# ---------------- Main ---------------- #
async def main():
    tasks = [asyncio.create_task(onliner(u)) for u in tokens_usernames]
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

try:
    print_banner()
    asyncio.run(main())
except KeyboardInterrupt:
    print_stopping_banner()

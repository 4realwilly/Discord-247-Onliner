# Discord 24/7 Onliner

**Last Updated:** 2025-09-22

**Disclaimer:**  
This tool interacts with the Discord Gateway and may technically violate Discord’s Terms of Service if misused. You should **not use it as a Discord RPC, bot, or automation that spams or breaks Discord rules**.  
Use at your own risk.  

Keep your Discord accounts online 24/7 with automatic reconnects, token rotation, and a clean color-coded logging system.  
Built with Python, WebSockets, and the official Discord Gateway.

---

<details>
<summary>Features</summary>

- Multi-account support (up to 10 tokens)  
- Color-coded logging system (Success, Info, Error)  
- Auto-reconnect on disconnects  
- Token rotation every X minutes/hours (from `.env`)  
- Live Discord API status in the banner  
- Per-token reconnect timers  
- Automatic invalid token detection  
- Clean scrolling log buffer (prevents console spam)  

</details>

---

<details>
<summary>Requirements</summary>

- Python 3.9+  

Install dependencies:

    pip install -r requirements.txt

[requirements.txt](https://github.com/4realwilly/Discord-247-Onliner/blob/main/requirements.txt)

</details>

---

<details>
<summary>Setup</summary>

Clone the repo:

    git clone https://github.com/4realwilly/Discord-247-Onliner.git
    cd Discord-247-Onliner

Fill out your `.env` file:  
[.env](https://github.com/4realwilly/Discord-247-Onliner/blob/main/.env)

    TOKEN1=your_token_here
    USERNAME1=AccountName
    STATUS1=idle

    TOKEN2=your_second_token_here
    USERNAME2=SecondAccount
    STATUS2=dnd

    # Retry delay in seconds between reconnect attempts
    RETRY_DELAY=15

    # Auto-rotate reconnect interval
    # Set ROTATE_MINUTES for fine-grain control (overrides ROTATE_HOURS)
    ROTATE_HOURS=0
    ROTATE_MINUTES=15

Run the script:  
[app.py](https://github.com/4realwilly/Discord-247-Onliner/blob/main/app.py)

    python app.py

</details>

---

<details>
<summary>Notes</summary>

- Invalid tokens are detected automatically and won’t crash the app.  
- Rotation interval is controlled via `.env`:  
  - `ROTATE_MINUTES` (fine control)  
  - `ROTATE_HOURS` (larger intervals)  
- Set rotation to `0` to disable auto-rotation.  
- Do not use as a bot or RPC — keep usage minimal to avoid account risk.  

</details>

---

<details>
<summary>Troubleshooting</summary>

- **`4004 Authentication failed`** → Your token is invalid or expired.  
- **Repeated `SSL connection is closed`** → Normal when Discord forces a reconnect. The script will automatically handle it.  
- **Banner shows fewer tokens loaded** → Some tokens are invalid or missing. Only valid tokens are used.  

</details>

---

<details>
<summary>Credits</summary>

- Original author: **William Holley**  
- Contact: **wholley123@icloud.com**  
- GitHub: [GitHub](https://github.com/4realwilly)  

Please give credit if you modify or redistribute the code.

</details>

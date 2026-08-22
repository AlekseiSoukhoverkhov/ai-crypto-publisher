# 🚀 FINXTEN — Dual-Language AI Crypto Publisher

An automated Python system that fetches real-time cryptocurrency quotes and news from RSS feeds, processes the data using Google Gemini, generates custom 3D thematic illustrations via FLUX.1 (Hugging Face), and publishes bilingual daily digests (English & Russian) to Telegram channels.

---

## 🛠️ Tech Stack & Features

* **AI Models:** Google GenAI SDK for post formatting and text generation.
* **Image Generation:** Hugging Face Hub (`black-forest-labs/FLUX.1-schnell`) for thematic 3D covers.
* **Integrations:** `pyTelegramBotAPI` for channel posting, CoinGecko API & RSS Parser for market data.
* **Automation:** Bash scheduler with built-in idempotency checks to prevent duplicate daily executions.

---

## 📂 Repository Layout

```text
finxten-bot/
├── main.py            # Main automation logic
├── run_bot.sh         # Cron execution wrapper & state guard
├── setup.sh           # Environment setup script
├── requirements.txt   # Python dependencies
├── .env.example       # API credentials template
└── README.md          # Complete project documentation
```

---

## ⚙️ Setup & Installation

### 1. Automated Setup
Clone the repository and run the setup script to prepare the Python virtual environment and install all required libraries:

```bash
git clone https://github.com/your-username/finxten-bot.git
cd finxten-bot
bash setup.sh
```

### 2. Manual Setup (Alternative)
If you prefer setting up the environment manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
chmod +x run_bot.sh
```

### 3. Configure Credentials
Open `.env` and fill in your API tokens:

```bash
nano .env
```

Set the variables inside `.env`:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
HF_TOKEN=your_huggingface_token_here

# English Channel Configuration
TG_BOT_TOKEN_EN=your_english_bot_token_here
CHAT_ID_EN=@finxten

# Russian Channel Configuration
TG_BOT_TOKEN_RU=your_russian_bot_token_here
CHAT_ID_RU=@finxten_ru
```

---

## 🚀 Execution & Automation

### Manual Run
To execute a test run manually:

```bash
./venv/bin/python main.py
```

### Automated Scheduling (Cron)
To set up daily execution at 08:00 AM and verify status on system reboot, add the following to `crontab -e`:

```cron
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

@reboot sleep 60 && /bin/bash /home/webmaster/finxten_bot/run_bot.sh
0 8 * * * /bin/bash /home/webmaster/finxten_bot/run_bot.sh
```

> 🛡️ **Execution Safety:** `run_bot.sh` records successful runs in `last_run.txt`. If triggered multiple times on the same day, it exits silently to prevent duplicate posts and token consumption.

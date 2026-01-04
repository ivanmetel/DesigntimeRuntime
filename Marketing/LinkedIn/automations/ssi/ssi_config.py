import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Marketing/
DATA_DIR = PROJECT_ROOT / "LinkedIn" / "data" / "ssi"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# API
LINKEDIN_SSI_ENDPOINT = "https://www.linkedin.com/api/ssi/profile"
LINKEDIN_TIMEOUT = 30

# Credentials (from .env)
LINKEDIN_TOKEN = os.getenv('LINKEDIN_TOKEN')

# Logs
LOG_FILE = DATA_DIR / "logs" / f"{datetime.now().strftime('%Y-%m-%d')}.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Slack / Telegram (optional, for errors only)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
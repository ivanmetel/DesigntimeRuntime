#!/usr/bin/env python3
"""
SSI Parser Job.
Scheduled to run monthly via GitHub Actions.

Flow:
  1. Fetch SSI from LinkedIn
  2. Render as Obsidian markdown
  3. Save to file
  4. Commit to Git
  5. Notify (if error)
"""

import sys
import subprocess
from datetime import datetime
from .io import fetch_ssi, save_markdown, save_json
from .render import render_obsidian_markdown, get_filename
from .config import LOG_FILE, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def log(message: str):
    """Print + write to log file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')

def notify_telegram(message: str):
    """Send error notification to Telegram (optional)"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': f"❌ SSI Parser Error\n\n{message}"
        }, timeout=5)
    except:
        pass  # Silent fail — не критично

def main():
    """Main job"""
    try:
        log("🚀 Starting SSI Parser")
        
        # 1. Fetch
        log("📥 Fetching SSI from LinkedIn...")
        ssi_data = fetch_ssi()
        log(f"✅ Fetched: SSI={ssi_data.ssi}/100")
        
        # 2. Render
        log("🎨 Rendering Obsidian markdown...")
        markdown = render_obsidian_markdown(ssi_data)
        filename = get_filename(ssi_data)
        log(f"✅ Rendered: {filename}")
        
        # 3. Save
        log("💾 Saving to file...")
        save_markdown(filename, markdown)
        save_json(filename, ssi_data)
        log(f"✅ Saved to {filename}")
        
        # 4. Git commit
        log("📝 Committing to Git...")
        subprocess.run([
            'git', 'add', f'Marketing/LinkedIn/data/ssi/{filename}'
        ], check=True)
        subprocess.run([
            'git', 'commit', '-m', f'SSI: {filename} (SSI={ssi_data.ssi})'
        ], check=True)
        subprocess.run(['git', 'push'], check=True)
        log("✅ Committed & pushed")
        
        log(f"✨ Job completed successfully")
        return 0
    
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        log(f"❌ Error: {error_msg}")
        notify_telegram(error_msg)
        return 1

if __name__ == '__main__':
    sys.exit(main())
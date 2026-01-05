#!/usr/bin/env python3
"""
job.py — SSI Parser Job with screenshot input and Google Drive upload
"""

import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from .io import fetch_ssi_from_screenshot, save_markdown, save_json, upload_to_google_drive
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
        pass  # Silent fail


def main(screenshot_path: str = None):
    """
    Main job
    
    Args:
        screenshot_path: Path to SSI screenshot (required)
    """
    try:
        if not screenshot_path:
            raise ValueError("Screenshot path is required")
        
        if not Path(screenshot_path).exists():
            raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")
        
        log("🚀 Starting SSI Parser")
        log(f"📸 Using screenshot: {screenshot_path}")
        
        # 1. Parse screenshot
        log("🔍 Parsing screenshot with Claude Vision...")
        ssi_data = fetch_ssi_from_screenshot(screenshot_path)
        log(f"✅ Parsed: SSI={ssi_data.ssi}/100")
        
        # 2. Render
        log("🎨 Rendering Obsidian markdown...")
        markdown = render_obsidian_markdown(ssi_data)
        filename = get_filename(ssi_data)
        log(f"✅ Rendered: {filename}")
        
        # 3. Save locally
        log("💾 Saving to file...")
        local_path = save_markdown(filename, markdown)
        save_json(filename, ssi_data)
        log(f"✅ Saved locally: {local_path}")
        
        # 4. Upload to Google Drive
        log("☁️  Uploading to Google Drive...")
        drive_file_id = upload_to_google_drive(local_path)
        log(f"✅ Uploaded to Drive: {drive_file_id}")
        
        # 5. Git commit (log only, not the markdown file)
        log("📝 Committing to Git...")
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        subprocess.run([
            'git', 'add', str(LOG_FILE)
        ], check=True)
        subprocess.run([
            'git', 'commit', '-m', f'SSI: executed successfully (SSI={ssi_data.ssi})'
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
    parser = argparse.ArgumentParser(description='SSI Parser')
    parser.add_argument('screenshot', help='Path to LinkedIn SSI screenshot')
    args = parser.parse_args()
    
    sys.exit(main(args.screenshot))

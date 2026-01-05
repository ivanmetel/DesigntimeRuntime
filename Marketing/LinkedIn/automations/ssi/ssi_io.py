"""
io.py — Fetch SSI from screenshot using Claude Vision + Google Drive upload
"""

import anthropic
import base64
import json
import os
from pathlib import Path
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .model import SSIData
from .config import DATA_DIR

def encode_image(image_path: str) -> str:
    """Encode image to base64"""
    with open(image_path, 'rb') as f:
        return base64.standard_b64encode(f.read()).decode('utf-8')


def fetch_ssi_from_screenshot(screenshot_path: str) -> SSIData:
    """
    Parse SSI screenshot using Claude Vision.
    
    Expected to find on page:
    - Current SSI score (0-100)
    - 4 components: brand, right_people, engagement, relationships (0-100 each)
    - Industry rank (top X%)
    - Network rank (top X%)
    - Industry average (0-100)
    - Network average (0-100)
    
    Args:
        screenshot_path: Path to LinkedIn SSI screenshot
        
    Returns:
        SSIData object
        
    Raises:
        FileNotFoundError: If screenshot doesn't exist
        ValueError: If Claude can't extract required fields
    """
    
    if not Path(screenshot_path).exists():
        raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")
    
    # Encode image
    image_data = encode_image(screenshot_path)
    
    # Use Claude Vision to parse
    client = anthropic.Anthropic()
    
    prompt = """
Analyze this LinkedIn SSI (Social Selling Index) screenshot and extract ALL numeric values.

Return ONLY a JSON object with these exact keys (no markdown, no explanation):
{
  "ssi": <current SSI score 0-100>,
  "brand": <Establish professional brand 0-100>,
  "right_people": <Find the right people 0-100>,
  "engagement": <Engage with insights 0-100>,
  "relationships": <Build relationships 0-100>,
  "industry_rank": <Top X% in industry (just the number, e.g. 72)>,
  "network_rank": <Top X% in network (just the number, e.g. 65)>,
  "industry_avg": <Industry average 0-100>,
  "network_avg": <Network average 0-100>
}

If you can't find a value, use null.
Only return valid JSON, nothing else.
"""
    
    message = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    
    # Parse response
    response_text = message.content[0].text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith('```'):
        response_text = response_text.split('```')[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    data = json.loads(response_text)
    
    # Validate required fields
    required = ['ssi', 'brand', 'right_people', 'engagement', 'relationships', 
                'industry_rank', 'network_rank', 'industry_avg', 'network_avg']
    
    missing = [k for k in required if data.get(k) is None]
    if missing:
        raise ValueError(f"Missing fields in screenshot: {missing}")
    
    # Create SSIData
    ssi = SSIData(
        date=datetime.now(),
        ssi=int(data['ssi']),
        brand=int(data['brand']),
        right_people=int(data['right_people']),
        engagement=int(data['engagement']),
        relationships=int(data['relationships']),
        industry_rank=int(data['industry_rank']),
        network_rank=int(data['network_rank']),
        industry_avg=float(data['industry_avg']),
        network_avg=float(data['network_avg'])
    )
    
    return ssi


def save_markdown(filename: str, content: str) -> str:
    """Save markdown to file"""
    filepath = DATA_DIR / filename
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)


def save_json(filename: str, data: SSIData) -> str:
    """Save SSI data as JSON (for backup)"""
    filepath = DATA_DIR / filename.replace('.md', '.json')
    filepath.write_text(json.dumps(data.to_dict(), indent=2), encoding='utf-8')
    return str(filepath)


def upload_to_google_drive(file_path: str, folder_id: str = None) -> str:
    """
    Upload file to Google Drive.
    
    Args:
        file_path: Local path to file
        folder_id: Google Drive folder ID (from env or config)
        
    Returns:
        Google Drive file ID
        
    Raises:
        ValueError: If credentials or folder_id missing
    """
    
    # Get credentials from env
    credentials_json = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
    if not credentials_json:
        raise ValueError("GOOGLE_DRIVE_CREDENTIALS not set in env")
    
    if not folder_id:
        folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    if not folder_id:
        raise ValueError("GOOGLE_DRIVE_FOLDER_ID not set in env")
    
    # Parse credentials
    credentials_dict = json.loads(credentials_json)
    credentials = Credentials.from_service_account_info(
        credentials_dict,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    
    # Build Drive service
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # Upload file
    file = Path(file_path)
    media = MediaFileUpload(file_path, mimetype='text/markdown')
    
    file_metadata = {
        'name': file.name,
        'parents': [folder_id]
    }
    
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    return uploaded_file.get('id')

import requests
import json
from datetime import datetime
from .model import SSIData
from .config import LINKEDIN_SSI_ENDPOINT, LINKEDIN_TOKEN, LINKEDIN_TIMEOUT, DATA_DIR

def fetch_ssi() -> SSIData:
    """
    Fetch SSI data from LinkedIn.
    Returns SSIData object or raises Exception on error.
    """
    headers = {
        'Authorization': f'Bearer {LINKEDIN_TOKEN}',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.get(
            LINKEDIN_SSI_ENDPOINT,
            headers=headers,
            timeout=LINKEDIN_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Parse API response → SSIData
        ssi = SSIData(
            date=datetime.now(),
            ssi=data['ssi']['score'],
            brand=data['components']['brand'],
            right_people=data['components']['find_right_people'],
            engagement=data['components']['engage_with_insights'],
            relationships=data['components']['build_relationships'],
            industry_rank=data['ranks']['industry_percentile'],
            network_rank=data['ranks']['network_percentile'],
            industry_avg=data['averages']['industry'],
            network_avg=data['averages']['network']
        )
        
        return ssi
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"LinkedIn API error: {str(e)}")
    except KeyError as e:
        raise Exception(f"Unexpected response format: {str(e)}")


def save_markdown(filename: str, content: str) -> str:
    """
    Save markdown to file.
    Returns full path to saved file.
    """
    filepath = DATA_DIR / filename
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)


def save_json(filename: str, data: SSIData) -> str:
    """
    Save SSI data as JSON (for backup).
    """
    filepath = DATA_DIR / filename.replace('.md', '.json')
    filepath.write_text(json.dumps(data.to_dict(), indent=2), encoding='utf-8')
    return str(filepath)
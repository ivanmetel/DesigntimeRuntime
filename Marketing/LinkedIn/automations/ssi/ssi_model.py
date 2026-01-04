from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SSIData:
    """LinkedIn SSI snapshot"""
    date: datetime
    ssi: int
    brand: int
    right_people: int
    engagement: int
    relationships: int
    industry_rank: int
    network_rank: int
    industry_avg: float
    network_avg: float
    
    def to_dict(self):
        """Convert to dict (for easy JSON serialization)"""
        d = asdict(self)
        d['date'] = self.date.strftime('%Y-%m-%d')
        return d
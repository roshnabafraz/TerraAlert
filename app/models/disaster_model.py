from dataclasses import dataclass
from typing import Optional


@dataclass
class DisasterReport:
    title: str
    content: str
    source: Optional[str] = None
    published_at: Optional[str] = None
    location: Optional[str] = None
    disaster_type: Optional[str] = None
    severity: Optional[str] = None

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "published_at": self.published_at,
            "location": self.location,
            "disaster_type": self.disaster_type,
            "severity": self.severity,
        }

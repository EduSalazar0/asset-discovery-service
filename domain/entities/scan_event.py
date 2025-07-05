import uuid
from pydantic import BaseModel

class ScanEvent(BaseModel):
    """Represents the data received from the 'scan.started' event."""
    scan_id: uuid.UUID
    domain_name: str
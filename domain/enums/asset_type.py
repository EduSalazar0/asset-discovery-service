from enum import Enum

class AssetType(str, Enum):
    SUBDOMAIN = "SUBDOMAIN"
    IP_ADDRESS = "IP_ADDRESS"
    SERVICE = "SERVICE"
    WEBSITE = "WEBSITE"
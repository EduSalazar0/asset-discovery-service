import logging
from typing import List
import shodan

from core.config import settings

logger = logging.getLogger(__name__)

class SubdomainFinder:
    """
    Uses the Shodan API to discover subdomains for a given domain name.
    """

    def __init__(self):
        try:
            self.api = shodan.Shodan(settings.SHODAN_API_KEY)
            logger.info("Shodan API client initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Shodan API client: {e}")
            self.api = None

    def find(self, domain_name: str) -> List[str]:
        if not self.api:
            logger.error("Shodan API is not initialized.")
            return []

        logger.info(f"Querying Shodan for subdomains of: {domain_name}")

        try:
            data = self.api.dns.domain_info(domain_name)
            subdomains = [f"{sub}.{domain_name}" for sub in data.get("subdomains", [])]
            logger.info(f"Found {len(subdomains)} subdomains for {domain_name}.")
            return subdomains
        except shodan.APIError as e:
            logger.error(f"Shodan API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during Shodan query: {e}")
            return []

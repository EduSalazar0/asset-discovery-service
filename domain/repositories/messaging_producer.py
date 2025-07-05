from abc import ABC, abstractmethod
from domain.entities.asset import Asset

class IMessagingProducer(ABC):
    """Abstract interface for a messaging producer."""

    @abstractmethod
    def publish_asset_discovered(self, asset: Asset) -> None:
        """Publishes an event indicating a new asset has been discovered."""
        pass
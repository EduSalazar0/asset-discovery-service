from abc import ABC, abstractmethod
from domain.entities.asset import Asset

class IAssetRepository(ABC):
    """Abstract interface for asset data persistence."""

    @abstractmethod
    def save(self, asset: Asset) -> Asset:
        """Saves an asset entity."""
        pass
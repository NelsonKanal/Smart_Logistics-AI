class SmartLogisticsError(Exception):
    """Base exception for SmartLogistics AI."""


class UnsupportedCityError(SmartLogisticsError):
    """Raised when a city is not supported."""


class InvalidShipmentError(SmartLogisticsError):
    """Raised when shipment information is invalid."""


class ShipmentNotFoundError(SmartLogisticsError):
    """Raised when a shipment cannot be found."""


class KnowledgeBaseError(SmartLogisticsError):
    """Raised when the knowledge base cannot be loaded."""
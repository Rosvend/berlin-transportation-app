"""
Custom exception classes for the Berlin Transport application
Following SOLID principles with specific, well-defined exceptions
"""


class BerlinTransportException(Exception):
    """Base exception for all Berlin Transport application errors"""
    
    def __init__(self, message: str, detail: str = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class BVGAPIException(BerlinTransportException):
    """Exception raised when BVG API calls fail"""
    
    def __init__(self, message: str, status_code: int = None, detail: str = None):
        super().__init__(message, detail)
        self.status_code = status_code


class CacheException(BerlinTransportException):
    """Exception raised for cache-related errors"""
    pass


class StationNotFoundException(BerlinTransportException):
    """Exception raised when a station is not found"""
    
    def __init__(self, station_id: str):
        message = f"Station with ID '{station_id}' not found"
        super().__init__(message)
        self.station_id = station_id


class InvalidQueryException(BerlinTransportException):
    """Exception raised for invalid query parameters"""
    
    def __init__(self, param_name: str, reason: str):
        message = f"Invalid parameter '{param_name}': {reason}"
        super().__init__(message)
        self.param_name = param_name


class ServiceUnavailableException(BerlinTransportException):
    """Exception raised when a required service is unavailable"""
    
    def __init__(self, service_name: str):
        message = f"Service '{service_name}' is currently unavailable"
        super().__init__(message)
        self.service_name = service_name

"""
Exception hierarchy for the Pharmacy Management System.
"""

class PMSError(Exception):
    """Base exception for all PMS errors."""
    pass

class ValidationError(PMSError):
    """Raised when user input fails validation."""
    pass

class AuthenticationError(PMSError):
    """Raised on login failure (bad credentials, locked or inactive account)."""
    pass

class AuthorizationError(PMSError):
    """Raised when an employee lacks permission for an action."""
    pass

class NotFoundError(PMSError):
    """Raised when a requested record is not found."""
    pass

class DuplicateError(PMSError):
    """Raised when a unique constraint would be violated."""
    pass

class InsufficientStockError(PMSError):
    """Raised when trying to allocate more non-expired stock than available."""
    def __init__(self, message: str, available: int = 0):
        super().__init__(message)
        self.available = available

class BusinessRuleError(PMSError):
    """Raised when a general business rule is violated."""
    pass

class DatabaseError(PMSError):
    """Raised on unexpected database failures."""
    pass

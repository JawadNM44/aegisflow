"""Custom exception classes for AEGISFLOW."""
class AegisFlowError(Exception):
    """Base exception for application errors."""
    pass

class InfrastructureError(AegisFlowError):
    """Raised when infrastructure simulation fails."""
    pass

class AgentError(AegisFlowError):
    """Raised when an agent encounters an unrecoverable error."""
    pass

class CerebrasAPIError(AegisFlowError):
    """Raised when Cerebras API call fails after all retries."""
    pass

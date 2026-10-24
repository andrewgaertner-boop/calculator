"""Custom exceptions for the calculator application."""


class CalculatorError(Exception):
    """Base exception for all calculator-related errors."""


class OperationError(CalculatorError):
    """Raised when an arithmetic operation cannot be completed."""


class ValidationError(CalculatorError):
    """Raised when user input fails validation."""


class ConfigurationError(CalculatorError):
    """Raised when configuration loading or validation fails."""


class HistoryError(CalculatorError):
    """Raised when history save/load operations fail."""

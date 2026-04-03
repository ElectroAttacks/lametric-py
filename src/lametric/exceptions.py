"""Custom exception types used by the LaMetric Python client."""


class LaMetricApiError(Exception):
    """Base exception for all errors raised by this LaMetric client."""


class LaMetricConnectionError(LaMetricApiError):
    """Raised when the client cannot connect to the LaMetric device or API."""


class LaMetricAuthenticationError(LaMetricApiError):
    """Raised when authentication with the LaMetric API fails."""


class LaMetricUnsupportedError(LaMetricApiError):
    """Raised when an operation is not supported by the target device or API."""

"""Custom exceptions for NI Measurement Plug-In Package Builder."""


class InvalidInputError(Exception):
    """Custom exception for invalid input from CLI."""

    def __init__(self, message):
        """Initialize exception.

        Args:
            message (str): The message to be displayed.
        """
        self.message = message
        super().__init__(self.message)

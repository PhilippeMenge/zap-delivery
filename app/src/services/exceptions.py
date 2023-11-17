class FunctionProcessingError(Exception):
    """### Exception raised when an error occurs while processing a function.

    Note that the message will be sent to OpenAI, so it should be in portuguese.
    """

    def __init__(self, message: str):
        self.message = message

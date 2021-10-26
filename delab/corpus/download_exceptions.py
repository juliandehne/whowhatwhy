class ConversationNotInRangeException(Exception):
    """Exception raised for errors in the input salary.

    Attributes:
        salary -- input salary which caused the error
        message -- explanation of the error
    """

    def __init__(self, conversation_size, message="Conversation downloaded is not in range"):
        self.conversation_size = conversation_size
        self.message = message
        super().__init__(self.message)

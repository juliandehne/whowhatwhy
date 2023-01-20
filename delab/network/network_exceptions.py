class ReplyGraphException(Exception):

    def __init__(self, conversation_size, message="Graph is malformed"):
        self.conversation_size = conversation_size
        self.message = message
        super().__init__(self.message)

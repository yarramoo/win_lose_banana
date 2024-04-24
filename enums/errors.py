class UnexpectedMessageTypeError(Exception):
    def __init__(self, message_type):
        self.message_type = message_type
        super().__init__(f"Unexpected message type: {message_type}")
class Context:
    def __init__(self, user_id: str = "", metadata: dict = None):
        self.user_id = user_id
        self.metadata = metadata or {}

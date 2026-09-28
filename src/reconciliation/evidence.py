class Evidence:
    def __init__(self, source, source_id, recorded_at, author, content, event_at=None):
        self.source = source
        self.source_id = source_id
        self.recorded_at = recorded_at
        self.event_at = event_at
        self.author = author
        self.content = content

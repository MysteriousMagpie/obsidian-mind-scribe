class _ChatCompletions:
    def create(self, *args, **kwargs):
        raise NotImplementedError("openai API not available in test environment")

class _Chat:
    def __init__(self):
        self.completions = _ChatCompletions()

chat = _Chat()
api_key = None

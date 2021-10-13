class FailedOnStartException(Exception):
    """Raised when project envs not properly setted"""

    def __init__(self, message='Failed on start'):
        self.message = message
        super().__init__(self.message)

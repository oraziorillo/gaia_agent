from functools import lru_cache

class Settings:
    _verbose = False

    @property
    def verbose(self):
        return self._verbose
    
    @verbose.setter
    def verbose(self, value: bool):
        self._verbose = value

@lru_cache
def get_settings() -> Settings:
    """
    Returns a singleton instance of the Settings class.
    This function uses caching to ensure that the same instance is returned
    every time it is called.
    """
    return Settings()
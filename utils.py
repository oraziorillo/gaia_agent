from settings import Settings, get_settings
_settings: Settings = get_settings()

from enum import Enum

class FileStrategy(Enum):
    TRANSCRIPTION = 0
    VISION = 1
    ASSISTANTS = 2

EXT_TO_STRATEGY = {
    ".mp3": FileStrategy.TRANSCRIPTION,
    ".wav": FileStrategy.TRANSCRIPTION,
    ".m4a": FileStrategy.TRANSCRIPTION,
    ".jpg": FileStrategy.VISION,
    ".jpeg": FileStrategy.VISION,
    ".png": FileStrategy.VISION,
    ".webp": FileStrategy.VISION,
    ".gif": FileStrategy.VISION,
    ".py": FileStrategy.ASSISTANTS,
    ".xlsx": FileStrategy.ASSISTANTS,
    ".csv": FileStrategy.ASSISTANTS,
}

def get_filename_ext(file_name: str):
    return f".{file_name.split('.')[-1]}"

def vprint(*args, **kwargs):
    """
    Print the arguments only if the verbose setting is enabled.
    """
    if _settings.verbose:
        print(*args, **kwargs)
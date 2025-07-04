from settings import Settings, get_settings
_settings: Settings = get_settings()

def get_filename_ext(file_name: str):
    return f".{file_name.split('.')[-1]}"

def vprint(*args, **kwargs):
    """
    Print the arguments only if the verbose setting is enabled.
    """
    if _settings.verbose:
        print(*args, **kwargs)
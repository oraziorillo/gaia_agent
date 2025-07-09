TOOL_REGISTRY = {}

def register_tool(**kwargs):
    """
    Decorator that registers a function as a tool in the TOOL_REGISTRY.
    
    Args:
        **kwargs: Metadata to be stored with the function
        
    Returns:
        Decorated function with metadata stored in _as_tool attribute
    """
    def tool_wrapper(func):
        # Add the function to the registry with its name as the key
        TOOL_REGISTRY[func.__name__] = func
        
        # Store the metadata in the function's _as_tool attribute
        func._as_tool = kwargs
        
        return func
    
    return tool_wrapper
    
def tool(**kwargs):
    """
    Decorator that attaches metadata to a function via the _as_tool attribute.
    
    Args:
        **kwargs: Metadata to be stored with the function
        
    Returns:
        Decorated function with metadata stored in _as_tool attribute
    """
    def tool_wrapper(func):
        kwargs["type"] = "function"
        kwargs["name"] = func.__name__
        func._as_tool = kwargs
        return func
    return tool_wrapper
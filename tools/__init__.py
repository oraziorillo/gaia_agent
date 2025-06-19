import importlib
from langchain_core.runnables import Runnable

__all__ = ['tavily_search_tool', 'wikipedia_retriever_tool']

def __getattr__(tool_name: str) -> Runnable:
    if tool_name in __all__:
        module_name = tool_name.rstrip("_tool")
        module = importlib.import_module(f'.{module_name}', __name__)
        return getattr(module, tool_name)
    raise AttributeError(f"module {__name__}.{module_name} has no attribute {tool_name}")
# Imports all the tools in the tools directory
import tools.calculator
import tools.wikipedia_retrieval
import tools.web_search
import tools.youtube_video_analysis

from tools.tool_registry import TOOL_REGISTRY
__all__ = ['TOOL_REGISTRY'] # Expose only the TOOL_REGISTRY

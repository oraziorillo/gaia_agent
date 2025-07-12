# Imports all the tools in the tools directory
from tools.calculator import evaluate_expression
from tools.wikipedia_retrieval import wikipedia_page_search, wikipedia_page_sections_retriever, wikipedia_section_content_retriever
from tools.web_search import web_search
from tools.youtube_video_analysis import analyze_youtube_video

TOOL_REGISTRY = {
    evaluate_expression.__name__: evaluate_expression,
    wikipedia_page_search.__name__: wikipedia_page_search,
    wikipedia_page_sections_retriever.__name__: wikipedia_page_sections_retriever,
    wikipedia_section_content_retriever.__name__: wikipedia_section_content_retriever,
    web_search.__name__: web_search,
    analyze_youtube_video.__name__: analyze_youtube_video,
}

__all__ = ['TOOL_REGISTRY'] # Expose only the TOOL_REGISTRY

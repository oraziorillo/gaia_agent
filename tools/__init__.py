from .calculator import evaluate_expression
from .wikipedia_retrieval import (
    wikipedia_page_search,
    wikipedia_page_sections_retriever,
    wikipedia_section_content_retriever,
    wikipedia_similarity_retriever,
)
from .web_search import web_search
from .youtube_video_analysis import analyze_youtube_video

TOOL_REGISTRY = {
    "evaluate_expression": evaluate_expression,
    "wikipedia_page_search": wikipedia_page_search,
    "wikipedia_page_sections_retriever": wikipedia_page_sections_retriever,
    "wikipedia_section_content_retriever": wikipedia_section_content_retriever,
    "wikipedia_similarity_retriever": wikipedia_similarity_retriever,
    "web_search": web_search,
    "analyze_youtube_video": analyze_youtube_video,
}
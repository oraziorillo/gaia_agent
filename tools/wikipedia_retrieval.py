import wikipedia
from bs4 import BeautifulSoup
from tools.tool import tool

pages_cache: dict[str, wikipedia.WikipediaPage] = {}

@tool(
    description = "Tool that searches for a Wikipedia page based on a query.",
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search for a Wikipedia page."
            }
        },
        "required": ["query"]
    }
)
def wikipedia_page_search(query: str):
    return wikipedia.search(query)

    
@tool(
    description = "Tool that retrieves the sections of a specific Wikipedia page. After you have retrieved the page title, use this tool to retrieve the sections of the page.",
    parameters = {
        "type": "object",
        "properties": {
            "page_title": {
                "type": "string",
                "description": "The title of the Wikipedia page to retrieve the sections from."
            }
        },
        "required": ["page_title"]
    }
)
def wikipedia_page_sections_retriever(page_title: str):
    try:
        page = wikipedia.page(title=page_title, auto_suggest=False)
        pages_cache[page.title] = page
        return "Page title: " + page.title + "\nSections:" + str(_get_page_sections(page))
    except wikipedia.DisambiguationError as e:
        return "Disambiguation required. Call this tool again with one of the following options: " + str(e.options)


@tool(
    description = "Tool that retrieves the content of a specific section of a specific Wikipedia page.",
    parameters = {
        "type": "object",
        "properties": {
            "page_title": {
                "type": "string",
                "description": "The title of the Wikipedia page to retrieve the section content from."
            },
            "section_title": {
                "type": "string",
                "description": "The title of the section to retrieve the content from."
            }
        },
        "required": ["page_title", "section_title"]
    }
)
def wikipedia_section_content_retriever(page_title: str, section_title: str):
    try:
        page = pages_cache[page_title]
        return page.section(section_title)
    except KeyError:
        return "Page not found in cache. Please use the correct page title as returned by the wikipedia_page_sections_retriever tool."
    

def _get_page_sections_from_html(page_html: str) -> list[str]:
    soup = BeautifulSoup(page_html, 'html.parser')
    h2s = soup.find_all('h2')
    return [h2.text for h2 in h2s]


def _get_page_sections(page: wikipedia.WikipediaPage):
    if page.sections:
        return str(page.sections)
    else:
        return _get_page_sections_from_html(page.html())
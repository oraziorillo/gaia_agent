import requests
from bs4 import BeautifulSoup
from langchain.tools import tool

@tool
def fetch_text_content(url):
    """
    Fetch and return the textual content of a web page.
    
    Args:
        url (str): The URL to fetch content from
        
    Returns:
        str: The text content of the page
        
    Raises:
        requests.RequestException: If the request fails
        Exception: For other errors during processing
    """
    try:
        # Set a user agent to avoid being blocked by some sites
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Fetch the page content
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse HTML and extract text
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch URL: {e}")
    except Exception as e:
        raise Exception(f"Error processing content: {e}")
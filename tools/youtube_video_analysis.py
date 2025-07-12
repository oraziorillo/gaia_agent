from google import genai
from google.genai.types import Part, Content, FileData
from tools.tool import tool

client = genai.Client(vertexai=False)

@tool(
    description = "Analyzes the content of a YouTube video and answers a question about it.",
    parameters = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The specific question to ask about the content of the YouTube video."
            },
            "youtube_url": {
                "type": "string",
                "description": "The URL of the YouTube video to analyze."
            }
        },
        "required": ["question", "youtube_url"]
    }    
)
def analyze_youtube_video(question: str, youtube_url: str):
    response = client.models.generate_content(
        model='models/gemini-2.0-flash',
        contents=Content(
            parts=[
                Part(
                    file_data=FileData(file_uri=youtube_url)
                ),
                Part(text=question)
            ]
        )
    )
    return response.text
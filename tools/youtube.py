from google import genai
from google.genai.types import Part, Content, FileData


client = genai.Client(vertexai=False)

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
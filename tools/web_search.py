import os
from openai import OpenAI
from tools.tool import tool

@tool(
    description = "Answers a question by searching the information on the web. Instructions: Ask for a specific information in form of a question.",
    parameters = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that you need to be answered with the information on the web."
            }
        },
        "required": ["question"]
    }   
)
def web_search(question: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))    
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="Answer the question of the user based on the web search results. Make sure your answer is grounded in the information you find on the web. If you cannot find the information, say so. Don't be too verbose, answer the question in a concise manner.",
        input=question,
        tools=[{"type": "web_search_preview"}],
        tool_choice="required",  # Let the model decide when to use tools.
        temperature=0,       # Set temperature to 0 for deterministic and focused outputs.
        store=False
    )
    return response.output_text
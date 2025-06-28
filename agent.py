import os
from dotenv import load_dotenv
# Load environment variables from a .env file, which is where the OpenAI API key is stored.
load_dotenv(override=True)

import json
from openai import OpenAI
from typing import Optional

from utils import get_filename_ext

# Import all tools from their respective modules.
# This centralized import makes it easy to add or remove tools.
from tools.calculator import evaluate_expression
from tools.wikipedia import wikipedia_page_retriever
from tools.web_search import web_search

# Define the system prompt that guides the AI's behavior.
# This prompt instructs the model on how to structure its responses,
# ensuring the final output is in a consistent and parsable format.
INSTRUCTIONS = "You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER]. YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."

def call_function(name, args):
    if name == "evaluate_expression":
        return evaluate_expression(**args)
    if name == "wikipedia_page_retriever":
        return wikipedia_page_retriever(**args)
    if name == "web_search":
        return web_search(**args)
    if name == "programmer":
        return write_and_run_code(**args)

class GAIAAgent:
    """
    This class implements a ReAct (Reasoning and Acting) agent that uses the OpenAI API.
    It orchestrates a conversation with an AI model, allowing it to use tools to answer questions.
    """

    def __init__(self, model: str = "gpt-4.1"):
        """
        Initializes the agent.

        Args:
            model (str): The name of the OpenAI model to use.
        """
        # Initialize the OpenAI client, which is the main interface for interacting with the API.
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        
        # Convert the LangChain tools into the JSON schema format that the OpenAI API expects.
        # This schema informs the model about the available tools, their names, descriptions, and arguments.
        self.tools = [
            # Calculator tool
            {
                "type": "function",
                "name": "evaluate_expression",
                "description": "Perform mathematical calculations safely. This tool can handle:\n- Basic arithmetic: +, -, *, /, %, //, **\n- Mathematical functions: sqrt, sin, cos, tan, log, exp, etc.\n- Constants: pi, e, tau, inf\n- Functions: abs, round, min, max, sum, factorial\n\nExamples:\n- \"2 + 3 * 4\" -> 14\n- \"sqrt(16)\" -> 4.0\n- \"sin(pi/2)\" -> 1.0",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression as a string."
                        }
                    },
                    "required": ["expression"]
                }
            },
            # Wikipedia tool
            {
                "type": "function",
                "name": "wikipedia_page_retriever",
                "description": "Tool that fetches any pages from Wikipedia.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for Wikipedia."
                        }
                    },
                    "required": ["query"]
                }
            },
            # Web search tool
            {
                "type": "function",
                "name": "web_search",
                "description": "Answers a question by searching the information on the web. Instructions: Ask for a specific information in form of a question.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question that you need to be answered with the information on the web."
                        }
                    },
                    "required": ["question"]
                }
            }
        ]

        self.history = []

    def __call__(self, question: str, file_name: Optional[str] = "", file_bytes: Optional[bytes] = None, max_iterations: int = 10) -> str:
        """
        Executes the ReAct loop to answer a user's question.

        Args:
            question (str): The user's question.
            max_iterations (int): The maximum number of tool-use iterations to prevent infinite loops.

        Returns:
            str: The final answer from the AI model.
        """
        print(f"Agent received question: {question}")

        if file_name and get_filename_ext(file_name) in [".png", ".jpg"]:
            file = self.client.files.create(
                file=file_bytes,
                purpose="vision"
            )
            user_content = [
                {
                    "type": "input_image",
                    "file_id": file.id,
                },
                {
                    "type": "input_text",
                    "text": question,
                },
            ]
        elif file_name and get_filename_ext(file_name) in [".py", ".xlsx"]:
            file = self.client.files.create(
                file=file_bytes,
                purpose="assistants"
            )
            container = self.client.containers.create(name="test", file_ids=[file.id])
            self.tools.append(
                {
                    "type": "code_interpreter",
                    "container": container.id
                }
            )
            user_content = question

        elif file_name and get_filename_ext(file_name) in [".mp3"]:
            transcript = self.client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=file_bytes
            )
            user_content = f"{question}\n\nHere is the transcript of the audio file: \"{transcript.text}\""
        else:
            file = None
            user_content = question

        # Start the conversation with the system prompt and the user's question.
        history = [
            {"role": "developer", "content": INSTRUCTIONS},
            {"role": "user", "content": user_content}
        ]

        # The main loop for the agent's reasoning and acting process.
        for i in range(max_iterations):
            print(f"Iteration {i+1}...")
            # Call the OpenAI Chat Completions API with the current conversation history and available tools.
            response = self.client.responses.create(
                model=self.model,
                input=history,
                tools=self.tools,
                tool_choice="auto",  # Let the model decide when to use tools.
                temperature=0,       # Set temperature to 0 for deterministic and focused outputs.
                store=False
            )
            
            response_outputs = response.output

            no_tool_calls = True
            for output in response_outputs:
                if output.type != "function_call":
                    print(f"  - {output.type}")
                    continue

                no_tool_calls = False

                tool_name = output.name
                tool_args = json.loads(output.arguments)

                print(f"  - Calling tool: {tool_name} with args: {tool_args}")

                result = call_function(tool_name, tool_args)
                print(f"    Result: {result}")
                
                history.append(output)
                history.append({
                    "type": "function_call_output",
                    "call_id": output.call_id,
                    "output": str(result)
                })

            if no_tool_calls:
                final_answer = response.output_text
                print(f"Agent returning final answer: {final_answer}")
                if file: self.client.files.delete(file.id)
                return final_answer

        if file: self.client.files.delete(file.id)
        return "No answer found."

# For direct testing of the agent.
if __name__ == '__main__':
    agent = GAIAAgent()
    # Example question to test the agent's capabilities.
    question = "What is the square root of the number of letters in the name of the current US president?"
    answer = agent(question)
    print("---")
    print(f"Question: {question}")
    print(f"Final Answer: {answer}")
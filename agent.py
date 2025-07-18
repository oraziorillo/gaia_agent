import json
import os
import traceback
from openai import OpenAI

from utils import FileStrategy, get_filename_ext, vprint, EXT_TO_STRATEGY

# Import all tools from their respective modules.
from tools import TOOL_REGISTRY

# Define the system prompt that guides the AI's behavior.
# This prompt instructs the model on how to structure its responses,
# ensuring the final output is in a consistent and parsable format.
INSTRUCTIONS = "You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER]. YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."

def _call_function(name, args) -> str:
    """
    Dispatches function calls to the appropriate tool based on the function name.
    
    Args:
        name (str): The name of the function/tool to call.
        args (dict): Dictionary of arguments to pass to the function.
        
    Returns:
        str: The result from the called function.
    """
    return TOOL_REGISTRY[name](**args)

class GAIAAgent:
    """
    This class implements a ReAct (Reasoning and Acting) agent that uses the OpenAI API.
    It orchestrates a conversation with an AI model, allowing it to use tools to answer questions.
    """

    def __init__(self, model: str = "gpt-4.1-mini"):
        """
        Initializes the agent.

        Args:
            model (str): The name of the OpenAI model to use.
        """
        # Initialize the OpenAI client, which is the main interface for interacting with the API.
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        
        # This schema informs the model about the available tools, their names, descriptions, and arguments.
        self.tools = [
            func._as_tool for func in TOOL_REGISTRY.values()
        ]

        # Initialize conversation history for potential multi-turn conversations
        self.history = []

    def __call__(
        self,
        question: str, 
        file_path: str, 
        max_iterations: int = 10
    ) -> str:
        """
        Executes the ReAct loop to answer a user's question.

        Args:
            question (str): The user's question.
            file_path (str): The path to the file passed as input if it exists.
            max_iterations (int): The maximum number of tool-use iterations to prevent infinite loops.

        Returns:
            str: The final answer from the AI model.
        """
        vprint(f"> Agent received question: {question}")

        try:            
            if file_path:
                user_content = [
                    self._handle_file(file_path),
                    {
                        "type": "input_text",
                        "text": question
                    }
                ]

            else:
                # No file provided or unsupported file type
                user_content = question

            # Start the conversation with the system prompt and the user's question.
            history = [
                {"role": "developer", "content": INSTRUCTIONS},
                {"role": "user", "content": user_content}
            ]

            # The main loop for the agent's reasoning and acting process.
            for i in range(max_iterations):
                vprint(f"{' ' * 2}Iteration {i+1}...")
                # Call the OpenAI Response API with the current conversation history and available tools.
                response = self.client.responses.create(
                    model=self.model,
                    input=history,
                    tools=self.tools,
                    tool_choice="auto",  # Let the model decide when to use tools.
                    temperature=0,       # Set temperature to 0 for deterministic and focused outputs.
                    store=False
                )
                
                response_outputs = response.output

                # Check if any function calls were made in this iteration
                no_tool_calls = True
                for output in response_outputs:
                    # Skip non-function outputs (like text responses)
                    if output.type != "function_call":
                        vprint(f"{' ' * 4}- {output.type}")
                        continue

                    # We found at least one function call
                    no_tool_calls = False

                    # Extract function call details
                    tool_name = output.name
                    tool_args = json.loads(output.arguments)

                    vprint(f"{' ' * 4}- Calling tool: {tool_name} with args: {tool_args}")

                    # Execute the function call
                    result = _call_function(tool_name, tool_args)
                    
                    # Truncate very long results for logging purposes
                    max_line_length = 120
                    if len(result) < max_line_length:
                        vprint(f"{' ' * 6}Result: {repr(result)}")
                    else:
                        postfix = " [...]" if result[max_line_length - 1].isalnum() else "[...]"
                        vprint(f"{' ' * 6}Result: {repr(result[:max_line_length] + postfix)}")
                    
                    # Add the function call and its result to conversation history
                    history.append(output)
                    history.append({
                        "type": "function_call_output",
                        "call_id": output.call_id,
                        "output": str(result)
                    })

                # If no tools were called, the model has provided a final answer
                if no_tool_calls:
                    answer = response.output_text
                    vprint(f"{' ' * 2}Answer: {repr(answer)}")
                    # Extract the final answer from the model's response
                    final_answer = answer.split("FINAL ANSWER:")[-1].strip()
                    return final_answer

            return "No answer found."
    
        except Exception as e:
            print(traceback.format_exc())
            return "No answer found."
        
        finally:
            self._cleanup()

    def _handle_file(self, file_path: str) -> dict:
        """
        Handles the file passed as input.

        Returns:
            dict: A dictionary containing the additional content to be passed to the model.
        """
        # Handle different file types by preparing appropriate content format
        if EXT_TO_STRATEGY[get_filename_ext(file_path)] == FileStrategy.VISION:
            # For image files: upload for vision processing
            file = self.client.files.create(
                file=open(file_path, "rb"),
                purpose="vision"
            )
            return {
                "type": "input_image",
                "file_id": file.id,
            }
        
        elif EXT_TO_STRATEGY[get_filename_ext(file_path)] == FileStrategy.TRANSCRIPTION:
            # For audio files: transcribe and include transcript in the question
            transcript = self.client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=open(file_path, "rb"),
                temperature=0
            )
            return {
                "type": "input_text",
                "text": f"### Transcript of the audio file: \"{transcript.text}\""
            }

        else:
            # For code/data files: create a container for code interpretation
            file = self.client.files.create(
                file=open(file_path, "rb"),
                purpose="assistants"
            )
            container = self.client.containers.create(name="code_interpreter")
            self.tools.append(
                {
                    "type": "code_interpreter",
                    "container": container.id
                }
            )
            return {
                "type": "input_file",
                "file_id": file.id
            }
            
    def _cleanup(self):
        """
        Cleans up any resources used by the agent, such as uploaded files or containers.
        """
        # Delete all uploaded files
        for file in self.client.files.list():
            self.client.files.delete(file.id)
        
        # Delete all containers
        for container in self.client.containers.list():
            self.client.containers.delete(container.id)
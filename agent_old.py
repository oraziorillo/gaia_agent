import os
import json
from openai import OpenAI

from dotenv import load_dotenv
from langchain_core.utils.function_calling import convert_to_openai_tool

# Import all tools from their respective modules.
# This centralized import makes it easy to add or remove tools.
from tools import tavily as tavily_tools
from tools import wikipedia as wikipedia_tools
from tools import web_scraper
from tools import calculator

# Load environment variables from a .env file, which is where the OpenAI API key is stored.
load_dotenv(override=True)

# Define the system prompt that guides the AI's behavior.
# This prompt instructs the model on how to structure its responses,
# ensuring the final output is in a consistent and parsable format.
SYSTEM_PROMPT = "You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER]. YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."

class GAIAAgent:
    """
    This class implements a ReAct (Reasoning and Acting) agent that uses the OpenAI API.
    It orchestrates a conversation with an AI model, allowing it to use tools to answer questions.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initializes the agent.

        Args:
            model (str): The name of the OpenAI model to use.
        """
        # Initialize the OpenAI client, which is the main interface for interacting with the API.
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        
        # Consolidate all available tools into a single list.
        # LangChain's @tool decorator adds the necessary metadata for conversion.
        self._tools = [
            tavily_tools.tavily_search,
            wikipedia_tools.wikipedia_page_retriever,
            web_scraper.fetch_text_content,
            calculator.evaluate_expression
        ]
        
        # Create a mapping from tool names to the actual callable tool functions.
        # This allows for dynamic dispatch of tool calls based on the model's request.
        self.tool_map = {tool.name: tool for tool in self._tools}

        # Convert the LangChain tools into the JSON schema format that the OpenAI API expects.
        # This schema informs the model about the available tools, their names, descriptions, and arguments.
        self.openai_tools = [convert_to_openai_tool(tool) for tool in self._tools]

    def __call__(self, question: str, max_iterations: int = 5) -> str:
        """
        Executes the ReAct loop to answer a user's question.

        Args:
            question (str): The user's question.
            max_iterations (int): The maximum number of tool-use iterations to prevent infinite loops.

        Returns:
            str: The final answer from the AI model.
        """
        print(f"Agent received question: {question}")
        
        # Start the conversation with the system prompt and the user's question.
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

        # The main loop for the agent's reasoning and acting process.
        for i in range(max_iterations):
            print(f"Iteration {i+1}...")
            
            # Call the OpenAI Chat Completions API with the current conversation history and available tools.
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.openai_tools,
                tool_choice="auto",  # Let the model decide when to use tools.
                temperature=0,      # Set temperature to 0 for deterministic and focused outputs.
                seed=42,
                top_p=0.95
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # If the model requests to use tools, execute them.
            if tool_calls:
                # Add the model's response (with tool requests) to the conversation history.
                messages.append(response_message)
                
                # Execute each requested tool call.
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = self.tool_map.get(function_name)
                    
                    if function_to_call:
                        # The model returns arguments as a JSON string, so we need to parse it.
                        function_args = json.loads(tool_call.function.arguments)
                        
                        print(f"  - Calling tool: {function_name} with args: {function_args}")
                        
                        # Invoke the tool. The .invoke method is standard for LangChain tools.
                        # The arguments are passed as a dictionary.
                        function_response = function_to_call.invoke(function_args)

                        # Add the tool's output to the conversation history.
                        # This provides context for the model's next reasoning step.
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": str(function_response),
                            }
                        )
                    else:
                        print(f"  - Error: Tool '{function_name}' not found.")
            else:
                # If no tool calls are made, the model has provided its final answer.
                final_answer = response_message.content
                print(f"Agent returning final answer: {final_answer}")
                return final_answer
        
        # If the loop completes without a final answer, return an error message.
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
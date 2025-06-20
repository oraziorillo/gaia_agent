from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode
from langchain.prompts import ChatPromptTemplate

from chat_models import chat_gpt_4o_mini
from tools import tavily_search_tool, wikipedia_retriever_tool

SYSTEM_PROMPT = "You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER]. YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don’t use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don’t use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."

# Define the function that calls the model
def invoke_agent(state: MessagesState):
    response = main_runnable.invoke(state)
    # We return a list, because this will get added to the existing list
    return { "messages": [response] }

# Define the function that determines whether to continue or not
def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we respond to the user
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"

main_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{messages}"),
    ]
)

tools = [tavily_search_tool, wikipedia_retriever_tool]

llm_with_tools = chat_gpt_4o_mini.bind_tools(tools)
main_runnable = main_prompt | llm_with_tools 

workflow = StateGraph(MessagesState)

workflow.set_entry_point("agent")
workflow.add_node("agent", invoke_agent)
workflow.add_node("tools", ToolNode(tools))

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)
workflow.add_edge("tools", "agent")

graph = workflow.compile()
graph.name = "GAIA Agent"
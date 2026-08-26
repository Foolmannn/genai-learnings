
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

import asyncio

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")


# FOR MCP CLIENT / LIBRARY WE NEED THE ASYNCHRONOUS CODE. SO WE NEED TO CONVERT OUR SIMPLE TOOL BASED GRAPH TO THE ASYNC NATURE


# MCP client for local FastMCP server
client = MultiServerMCPClient(
    {
        "arith": {
            "transport": "stdio",
            "command": "python3",          
            "args": ["/Users/nitish/Desktop/mcp-math-server/main.py"],
        },
        "expense": {
            "transport": "streamable_http",  # if this fails, try "sse"
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        }
    }
)





class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

async def build_graph():

    tools = await client.get_tools()
    print(tools)

    llm_with_tools = llm.bind_tools(tools)

    async def chat_node(state: ChatState):
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools) # toolNode is internally asynchronous so we only need to convert the custom node as async 


    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")

    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge('tools', 'chat_node')

    chatbot = graph.compile()

    return chatbot

async def main():

    chatbot = await build_graph()
    userInput="Find the modulus of 100123123 and 23 . Then give the answer like an commentator ."


    response = await chatbot.ainvoke({'messages':[HumanMessage(content=userInput)]}) # ainvoke is the async invoke
    ai_message = response['messages'][-1].content[0]['text']
    print(ai_message)

if __name__== '__main__':
    asyncio.run(main())
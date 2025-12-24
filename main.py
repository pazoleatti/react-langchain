from typing import List

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from callbacks import AgentCallbackHandler

load_dotenv()


@tool
def get_text_length(text: str) -> int:
    """Returns the length of a text by characters"""
    print(f"get_text_length enter with {text=}")
    text = text.strip("\n").strip('"')  # stripping away non alphabetical characters
    return len(text)


def find_tool_by_name(tools: List[Tool], tool_name: str) -> Tool:
    for tool in tools:
        if tool.name == tool_name:
            return tool
    raise ValueError(f"Tool with name {tool_name} not found")


if __name__ == "__main__":
    tools = [get_text_length]

    llm = ChatOpenAI(temperature=0, callbacks=[AgentCallbackHandler()])
    llm_with_tools = llm.bind_tools(tools)

    messages = [HumanMessage(content="What is the length in characters of the text DOG?")]

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        print(response)

        if not response.tool_calls:
            # No more tool calls, we have the final answer
            print(f"Final Answer: {response.content}")
            break

        # Execute each tool call and add results as ToolMessages
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["args"]
            tool_to_use = find_tool_by_name(tools, tool_name)

            observation = tool_to_use.func(**tool_input)
            print(f"{observation=}")

            tool_message = ToolMessage(
                content=str(observation),
                tool_call_id=tool_call["id"]
            )
            messages.append(tool_message)

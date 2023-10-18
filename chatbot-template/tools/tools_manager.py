import os
from langchain.memory import ReadOnlySharedMemory
from langchain.agents import Tool, load_tools
from tools import kendra_retriever
from llms.llm_switcher import get_llm

tools_native = load_tools(["wikipedia", "llm-math"], llm=get_llm())

tools_custom = []

tools = tools_native + tools_custom

tool_names = [tool.name for tool in tools]
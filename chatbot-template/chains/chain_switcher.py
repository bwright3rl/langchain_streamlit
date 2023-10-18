import os
from dotenv import load_dotenv
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, initialize_agent
from langchain.agents import load_tools
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.agents.conversational.base import ConversationalAgent
from langchain.agents import initialize_agent
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.chains.question_answering import load_qa_chain
from llms.llm_switcher import get_llm
from prompts.agent_prompts import FORMAT_INSTRUCTIONS, PREFIX, SUFFIX, SYSTEM_MESSAGE, USER_MESSAGE
from llms.llm_switcher import get_llm
from tools.text_to_sql import run_query as text_to_sql_query
from tools.text_to_sql_snowflake import run_query as text_to_sql_snowflake
from tools.kendra_retriever import run_query as kendra_retriever
from tools.tools_manager import tools, tool_names
import pandas as pd


def run_chain(llm, chain, memory, prompt, df=None):
    
    response = None
    sources = None
    intermediate_steps = None
    
    if chain == 'Ask Kendra':
        response, sources = kendra_retriever(llm, memory, prompt)

    elif chain == 'Text-to-SQL':
        response, sources, intermediate_steps = text_to_sql(llm, prompt)

    elif chain == 'Text-to-SQL (Snowflake)':
        response, sources, intermediate_steps = text_to_sql_snowflake(llm, prompt)

    else:
        response, sources = kendra_retriever(llm, memory, prompt)
    
    return response, sources, intermediate_steps
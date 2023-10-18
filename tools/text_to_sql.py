import boto3
from langchain import SQLDatabase
from langchain.prompts.prompt import PromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine


connection_string = ""


def run_query(llm, query):

    _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then based on the table schema, question, SQL query, and SQL result, write a natural language response as an an answer to the question.  Do not mention the SQL query nor the SQL response to the Human. 

    Do not append 'Query:' to SQLQuery.
    
    Display SQLResult after the query is run in plain english that users can understand. 

    Provide answer in simple english statement.
 
    Only use the following tables:

    {table_info}

    "poutcome" means outcome.

    Question: {input}"""

    PROMPT_sql = PromptTemplate(
        input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
    )

    engine = create_engine(connection_string, echo=False)
    
    db = SQLDatabase(engine)

    db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=PROMPT_sql, verbose=True, return_intermediate_steps=True, use_query_checker=False)

    response = db_chain({"query": query}, return_only_outputs=True)

    return response['result'], None, response['intermediate_steps'][0]['input']
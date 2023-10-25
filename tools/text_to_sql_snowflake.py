import boto3
from langchain import SQLDatabase
from langchain.prompts.prompt import PromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv


def run_query(llm, query):

    load_dotenv()

    account = "ralphlauren"
    user = "CIX_REPORTING_USER_PROD"
    password = "Reporting@CIX-2023"
    warehouse = "CIX_REPORTING_PROD_WH"
    database = "CIX_PROD_DB"
    schema = "FOUNDATION"
    role = "CIX_DATA_ANALYST_PROD"

    engine = create_engine(
        URL(
            account=account,
            user=user,
            password=password,
            database=database,
            schema=schema,
            warehouse=warehouse,
            role=role,
        )
    )

    _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    
    When providing the SQLQuery, only respond with the SQL Query and nothing more.

    Do not append 'Query:' to SQLQuery.
    
    When provided the SQLResult after the query is run, provide the Answer in plain english natural-language that a regular human can understand.
    
    In the Answer, do NOT mention to the Human that you have been provided a SQLQuery or the SQLResult.
 
    Only use the following tables:

    {table_info}

    Question: {input}"""

    PROMPT_sql = PromptTemplate(
        input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
    )

    db = SQLDatabase(engine)

    db_chain = SQLDatabaseChain.from_llm(
        llm,
        db,
        prompt=PROMPT_sql,
        verbose=True,
        return_intermediate_steps=True,
        use_query_checker=False,
    )

    response = db_chain({"query": query}, return_only_outputs=True)

    return response["result"], None, response["intermediate_steps"][0]["input"]

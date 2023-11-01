from langchain.prompts import ChatPromptTemplate
from langchain.utilities import SQLDatabase
import boto3
from langchain import PromptTemplate, SQLDatabase
from langchain.prompts.prompt import PromptTemplate
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine
from operator import itemgetter
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda, RunnableMap
from langchain.utilities import SQLDatabase
from snowflake.sqlalchemy import URL

#adding some comments here to test how the dataiku library sync works

account = "ralphlauren-ralphlauren"
user = "CIX_REPORTING_USER_PROD"
password = "Reporting@CIX-2023"
warehouse = "CIX_REPORTING_PROD_WH"
database = "CIX_PROD_DB"
schema = "PUBLISHED"
role = "CIX_DATA_ANALYST_PROD"

engine = create_engine(URL(
    account = account,
    user = user,
    password = password,
    database = database,
    schema = schema,
    warehouse = warehouse,
    role = role
))

db = SQLDatabase(engine)


def get_schema(_):
    return db.get_table_info()


def get_dialect(_):
    return db.dialect


def convert_intermediate_steps(question, response):
    sql_query = response["query"]
    sql_response = response["response"]
    sql_dialect = response["dialect"]
    sql_schema = response["schema"]
    
    intermediate_steps = f"""Question: {question}\n\nSQL Query:{sql_query}\n\nSQL Response: {sql_response}"""
    
    # Show dialect, schema, and sample queries
    # intermediate_steps = intermediate_steps + "\n\nDialect: " + sql_dialect + "\n\nSchema:" + sql_schema
    
    return intermediate_steps


def run_query(llm, query):
 
    # Define prompt to generate an SQL query
    template_prompt_sql_query = """Based on the table schema and sample rows below, write a syntactically correct {dialect} SQL query that would answer the user's question:
    {schema}

    {question} 
    
    You should put all column names in double quotation marks, for example "label_code" or "year".
    You should not put table names in quotation marks, for example langchain_test_data.

    An example query you should output is:
    SELECT count(distinct("label_code")) FROM SNOWFLAKE_SANDBOX_LANGCHAIN_TEST

    Only respond with the SQL Query and nothing more.
    
    """
    
    # Create a ChatPromptTemplate from the prompt
    prompt_sql_query = ChatPromptTemplate.from_template(template_prompt_sql_query)

    # Define a chain that generates an SQL query using LangChain espression language, and ru
    sql_query_inputs = {
        "dialect": RunnableLambda(get_dialect),
        "schema": RunnableLambda(get_schema),
        "question": itemgetter("question")
    }
    sql_query = (
        RunnableMap(sql_query_inputs)
        | prompt_sql_query
        | llm.bind(stop=["\nSQLResult:"])
        | StrOutputParser()
    )

    # Define a prompt to interpret the results of the SQL query and generate a natural language response
    template_sql_response = """You are a helpful analyst. Based on the SQL response below, write a natural language response as an answer to the user's question. 
    Do not refer to SQL queries. Do not append anything to the front of the final answer, like 'Based on the SQL query and result provided, the answer to the question "which years do we have data for?" is:'

    Here is an example...
    Question: 'how many products have we sold?'
    SQLQuery: 'SELECT count(distinct("label_code")) FROM snowflake_sandbox_langchain_test'
    SQLResult: '[(150,)]'
    Answer: 'We have sold 150 products'

    Here is another example
    Question: 'how many years worth of data do we have?'
    SQLQuery: 'SELECT COUNT(DISTINCT("year")) FROM snowflake_sandbox_langchain_test'
    SQLResult: '[(3,)]'
    Answer: 'We have 3 years worth of data.'

    Now here is the actual answer we need you to generate...
    Question: {question}
    SQLQuery: {query}
    SQLResult: {response}
    Answer: """
    
    # Create a ChatPromptTemplate from the prompt
    prompt_sql_response = ChatPromptTemplate.from_template(template_sql_response)
    
    # Define a chan that interprets the results of the SQL query and generates a natural language response
    summarize_answer_inputs = {
        "schema": RunnableLambda(get_schema),
        "dialect": RunnableLambda(get_dialect),
        "question": itemgetter("question"),
        "query": itemgetter("query"),
        "response": itemgetter("response"),
    }
    summarize_answer = (
        RunnableMap(summarize_answer_inputs)
        | prompt_sql_response
        | llm
        | StrOutputParser()
    )

    # Define the entire chain that generates and runs the SQL query, and interprets the results
    full_chain = (
        RunnableMap({
            "question": itemgetter("question"),
            "query": sql_query,
        }) 
        | {
            "schema": RunnableLambda(get_schema),
            "dialect": RunnableLambda(get_dialect),
            "question": itemgetter("question"),
            "query": itemgetter("query"),
            "response": lambda x: db.run(x["query"])
        } 
        | {
            "schema": RunnableLambda(get_schema),
            "dialect": RunnableLambda(get_dialect),
            "question": itemgetter("question"),
            "query": itemgetter("query"),
            "response": itemgetter("response"),
            "answer": summarize_answer
        }
    )
    
    # Run the chain
    response = full_chain.invoke({"question": query})
    
    # Format intermediate steps
    intermediate_steps = convert_intermediate_steps(query, response)

    return response["answer"], None, intermediate_steps
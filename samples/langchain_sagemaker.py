from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json


sagemaker_endpoint_name = ''
region_name = 'us-east-1'

class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        input_str = json.dumps({"inputs": [[
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt},
        ]], "parameters": model_kwargs})
        print(input_str)
        return input_str.encode('utf-8')

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        print(response_json)
        return response_json[0]["generation"]["content"]

content_handler = ContentHandler()

llm = SagemakerEndpoint(
    endpoint_name = sagemaker_endpoint_name, 
    region_name = region_name, 
    model_kwargs = {
        "max_new_tokens": 1000, 
        "top_p": 0.9,
        "temperature": 0.6
    },
    endpoint_kwargs = {
        "CustomAttributes": "accept_eula=true"
    },
    content_handler = content_handler
)


prompt = PromptTemplate(
    template="You are an AI, please answer the question accurately: {input}", input_variables=["input"],
)

chain = LLMChain(llm=llm, prompt=prompt)

print(chain.run("Hello world"))
import os
import json
import openai
from langchain.llms.gpt4all import GPT4All
from langchain.llms.bedrock import Bedrock
from langchain.llms.sagemaker_endpoint import ContentHandlerBase, LLMContentHandler
from langchain.llms import SagemakerEndpoint
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from dotenv import load_dotenv

def get_llm():
    load_dotenv()
    llm = None
    
    if os.getenv("MODEL_PROVIDER") == 'bedrock':
        
        inference_modifier = {
            'max_tokens_to_sample': 1000, 
            "temperature":0.1,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman", "\n\nNew input:"]
        }
        
        llm = Bedrock(model_id = os.getenv("BEDROCK_MODEL_ID"), model_kwargs = inference_modifier)
        
        
    elif os.getenv("MODEL_PROVIDER") == 'sagemaker':

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
            endpoint_name = os.getenv("SAGEMAKER_ENDPOINT_NAME"), 
            region_name = os.getenv("SAGEMAKER_ENDPOINT_REGION"), 
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
        
    return llm
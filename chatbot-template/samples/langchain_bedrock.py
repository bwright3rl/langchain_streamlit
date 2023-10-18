from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

inference_modifier = {
    'max_tokens_to_sample': 1000, 
    "temperature":0,
    "top_k":250,
    "top_p":1,
    "stop_sequences": ["\n\nHuman", "\n\nNew input:"]
}

llm = Bedrock(model_id = 'anthropic.claude-v1', model_kwargs = inference_modifier)


prompt = PromptTemplate(
    template="You are an AI, please answer the question accurately: {input}", input_variables=["input"],
)

chain = LLMChain(llm=llm, prompt=prompt)

print(chain.run("Hello world"))
# Source:
# https://github.com/aws/amazon-sagemaker-examples/blob/main/introduction_to_amazon_algorithms/jumpstart-foundation-models/llama-2-text-completion.ipynb

from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

endpoint_name = ""
    
predictor = Predictor(endpoint_name, 
                      serializer=JSONSerializer(), deserializer=JSONDeserializer())

prompt = "Who are you?"
    
payload = {
    "inputs": [[
        {"role": "system", "content": ""},
        {"role": "user", "content": prompt},
    ]],
    "parameters": {
        "max_new_tokens": 1000,
        "top_p": 0.9,
        "temperature": 0.6,
        "return_full_text": True,
    },
}
  
def print_response(payload, response):
    print(payload["inputs"])
    print(response[0]["generation"]["content"])
    print("\n==================================\n")

try:
    response = predictor.predict(payload, custom_attributes="accept_eula=true")
    print_response(payload, response)
except Exception as e:
    print(e)
from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import RetrievalQA
import os


kendra_index_id = ""
user_context = {"Groups": [
    "data_science_team",
    "legal_compliance_team",
    ]}


def run_query(llm, memory, prompt):

    region = os.getenv("AWS_REGION")

    retriever = AmazonKendraRetriever(index_id = kendra_index_id, region_name = region, 
                                      user_context = user_context
                                      )
    
    # Workaround for memory not supporting a two output keys: 'result' and 'source_documents'
    memory.output_key = "result"
    
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, verbose=True, return_source_documents=True, memory=memory)

    result = qa({"query": prompt})
    
    unique_documents = {}
    for doc in result['source_documents']:
        source = doc.metadata['source']
        if source not in unique_documents:
            unique_documents[source] = doc.metadata

    # Now, unique_documents contains unique documents based on 'source'
    unique_documents_list = list(unique_documents.values())
    
    return result['result'], result['source_documents']
import os
import numpy as np
from dotenv import load_dotenv
import ast  # for converting embeddings saved as strings back to arrays
import openai  # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
from scipy import spatial  # for calculating vector similarities for search


# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
load_dotenv()

api_key = os.getenv('openapi_key') #Uncomment this and run the command.
openai.api_key = api_key

def create_embedding(context):
    try:
        response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input= context
        )
        embeddings = [item['embedding'] for item in response['data']]
        # flattened_embeddings = [value for sublist in embeddings for value in sublist]
        return embeddings 
    except Exception as e:
        print(f"Error in generating Embedding: {e}")
        return ""


# df = pd.read_csv('sec_pdfs_data.csv')
# df['embedding']=df['Context'].apply(create_embedding)
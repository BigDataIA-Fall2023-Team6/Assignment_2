import pandas as pd
import numpy as np
import openai
from sklearn.metrics.pairwise import cosine_similarity

# Load your embeddings from the CSV
df = pd.read_csv('sec_pdfs_embb.csv')

def search(query_embedding):
    # Calculate the cosine similarity between the query embedding and all context embeddings
    similarities = cosine_similarity([query_embedding], np.vstack(df['embedding'].to_list()))
    
    # Get the index of the most similar context
    top_idx = np.argmax(similarities)
    
    # Return the most similar context
    return df.iloc[top_idx]['Context']

def ask(question, context):
    # Use GPT-3.5-turbo to generate an answer based on the context
    response = openai.Completion.create(
        model="gpt-turbo-3.5-turbo",
        prompt=f"Question: {question}\nContext: {context}\nAnswer:",
        max_tokens=150,
        n=1,
        stop=["\n"],
        temperature=0.7,
    )
    
    return response.choices[0].text.strip()

def get_answer(question, query_embedding):
    context = search(query_embedding)
    answer = ask(question, context)
    return answer
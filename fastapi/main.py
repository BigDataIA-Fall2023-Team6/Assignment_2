from fastapi import FastAPI, Query
from pydantic import BaseModel
import tiktoken
from transformers import GPT2TokenizerFast
import spacy
import pandas as pd
import openai

app = FastAPI()


nlp = spacy.load("en_core_web_md")

df = []

api_key = ""
openai.api_key = api_key

class QueryRequest(BaseModel):
    question: str
    context: str



def num_tokens(text):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    encoding = tokenizer.encode(text, add_special_tokens=False)
    return len(encoding)

def query_message(query, text,  token_budget):
    strings, relatednesses = strings_ranked_by_relatedness(query, text)
    introduction = 'Use the relevant documents from the SEC government data to answer the subsequent question. If the answer cannot be found in the documents, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    remaining_budget = token_budget
    for string in strings:
        next_document = f'\n\nSEC Document Section:\n"""\n{string}\n"""'
        if num_tokens(message + next_document + question) > remaining_budget:
            message += question
            
            break
        else:
            message += next_document
    return message + question

def strings_ranked_by_relatedness(query, text, top_n=100):
    query_embedding = nlp(query)
    text_embeddings = [nlp(section) for section in text]
    similarities = [query_embedding.similarity(embedding) for embedding in text_embeddings]
    
    sorted_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)
    
    top_strings = [text[i] for i in sorted_indices[:top_n]]
    top_relatednesses = [similarities[i] for i in sorted_indices[:top_n]]
    
    return top_strings, top_relatednesses


def generate_context_from_summary(summary: str):
 
    sections = summary.split("\n") 


    filtered_sections = [section for section in sections if len(section.split()) > 40]

    if filtered_sections:
        
        data = {
            "text": filtered_sections
        }

        df = pd.DataFrame(data)

        
        print("Filtered Sections:")
        print(df)

        
        context = "\n".join(filtered_sections)

        return context
    else:
        print("No filtered sections found in the summary.")
        return "Unable to extract text from the PDF"

class SummaryRequest(BaseModel):
    summary: str
    
@app.post("/data-collection")
def data_collection(request_data: SummaryRequest ):
    global  context 
    context = generate_context_from_summary(request_data.summary)
    return {"context": context}

@app.post("/ask")
def ask_question(query_request: QueryRequest):
    query = query_request.question
    context = query_request.context
    token_budget = 4096 - 500
    message = query_message(query, context, token_budget)
    messages = [
        {"role": "system", "content": "You answer questions about SEC government data."},
        {"role": "user", "content": message},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0)
    response_message = response["choices"][0]["message"]["content"]
    print(df)
    return {"answer": response_message}


if __name__ == "__main__":
    import os

# Disable tokenizers parallelism
    os.environ["TOKENIZERS_PARALLELISM"] = "false"  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

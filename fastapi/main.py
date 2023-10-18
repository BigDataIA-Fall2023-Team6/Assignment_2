from fastapi import FastAPI, Query
from pydantic import BaseModel
import tiktoken
from transformers import GPT2TokenizerFast
import spacy
import pandas as pd
import openai
import requests
from io import BytesIO
import time
from pypdf import PdfReader
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()

api_key = os.getenv('openapi_key') #Uncomment this and run the command.

openai.api_key = api_key

nlp = spacy.load("en_core_web_md")

df = []

def pdf_url_summary(pdf_url):
    try:
        # Download the PDF file from the URL
        response = requests.get(pdf_url)
        response.raise_for_status()

        # Create a PDF file object from the downloaded content
        pdf_file = BytesIO(response.content)

        start_time=time.time()
        # Create a PDF reader object
        pdf_reader = PdfReader(pdf_file)

        end_time = time.time()

        # Initialize variables for summarization
        num_pages = len(pdf_reader.pages)
        total_chars = 0
        special_chars = set()
        

        # Initialize a variable to store the extracted text
        text = ''

        start_time2=time.time()
        # Iterate through each page and extract the text
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            text += page_text
            
            # Update character count and collect special characters
            total_chars += len(page_text)
            special_chars.update(char for char in page_text if not char.isalnum())
        
        end_time2=time.time()

        computation_time = end_time-start_time

        computation_time2= end_time2-start_time2

        # Create a summary dictionary
        summary = {
            "Number of Pages": num_pages,
            "Total Characters": total_chars,
            "Special Characters": ", ".join(special_chars),
            "Computation time (s) for PyReader ":round(computation_time,4),
            "Computation time (s) for Extract Text":round(computation_time2,4),
        }

        return text, summary

    except Exception as e:
        return f"An error occurred: {e}"

class QueryRequest(BaseModel):
    question: str
    context: str


class PdfLink(BaseModel):
    pdf_url: str
    ngrok_url:str

class PyPdfLink(BaseModel):
    pdf_url: str

@app.post("/convert_pdf")
def convert_pdf(pdf_link: PyPdfLink):
    pdf_url = pdf_link.pdf_url
    global context
    
    text, summary = pdf_url_summary(pdf_url)
    
    return {"text": text, "summary": summary}


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






@app.post("/nougatconvert_pdf")
def nougatconvert_pdf(data: PdfLink):
    pdf_url = data.pdf_url
    ngrok_url = data.ngrok_url
    global context
    text = pdf_url_summary_nougat(pdf_url,ngrok_url)
    return {"text": text}


def pdf_url_summary_nougat(pdf_url,ngrok_url):
    try:
        # Download the PDF file from the URL
        response = requests.get(pdf_url)
        response.raise_for_status()

        # Create a file-like object from the response content
        file_data = response.content

        # Prepare the file for uploading
        files = {'file': ('uploaded_file.pdf', file_data, 'application/pdf')}

        # Replace with the ngrok URL provided by ngrok
        ng_url = ngrok_url  # Replace with your ngrok URL

        # Send the POST request to the Nougat API via ngrok
        response = requests.post(f'{ng_url}/predict/', files=files, timeout=500)

        # Check if the request to the Nougat API was successful (status code 200)
        if response.status_code == 200:
            # Get the response content (Markdown text)
            markdown_text = response.text
            return markdown_text
        else:
            return f"Failed to make the request. Status Code: {response.status_code}"

    except Exception as e:
        return f"An error occurred: {e}"
    

if __name__ == "__main__":
    import os

    # Disable tokenizers parallelism
    os.environ["TOKENIZERS_PARALLELISM"] = "false"  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
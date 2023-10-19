from fastapi import FastAPI, Query
from pydantic import BaseModel
import os
from helper import *

app = FastAPI()

class PyPdfLink(BaseModel):
    pdf_url: str

class PdfLink(BaseModel):
    pdf_url: str
    ngrok_url:str

class SummaryRequest(BaseModel):
    summary: str

class QueryRequest(BaseModel):
    question: str
    context: str


@app.post("/convert_pdf")
def convert_pdf(pdf_link: PyPdfLink):
    pdf_url = pdf_link.pdf_url
    global context
    
    text, summary = pdf_url_summary(pdf_url)
    
    return {"text": text, "summary": summary}

@app.post("/nougatconvert_pdf")
def nougatconvert_pdf(data: PdfLink):
    pdf_url = data.pdf_url
    ngrok_url = data.ngrok_url
    global context
    text = pdf_url_summary_nougat(pdf_url,ngrok_url)
    return {"text": text}
    
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

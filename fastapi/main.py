from fastapi import FastAPI, Query
from pydantic import BaseModel
import os
from helper import *
from typing import Dict, List, Optional, Any, Union

app = FastAPI()
GPT_MODEL = "gpt-3.5-turbo"

class PyPdfLink(BaseModel):
    pdf_url: str

class PdfLink(BaseModel):
    pdf_url: str
    ngrok_url:str

class SummaryRequest(BaseModel):
    summary: str
    # dataframe: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    question: str
    context: str
    # dataframe: Dict[str, Any]


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
    # context = request_data.summary
    # df = request_data.dataframe
    global context 
    context = generate_context_from_summary(request_data.summary)  #context, df
    return {"context": context} # "dataframe": df.to_dict()

@app.post("/data-collection_nougat")
def data_collection(request_data: SummaryRequest ):
    global  context 
    context = generate_context_from_summary_nougat(request_data.summary)
    return {"context": context}

@app.post("/ask")
def ask_question(query_request: QueryRequest):
    query = query_request.question
    context = query_request.context
    token_budget = 4096 - 500
    message = query_message(query, context, token_budget)
    messages = [
        {"role": "system", "content": "You answer questions about SEC government data and provided context only"},
        {"role": "user", "content": message},
    ]
    response = openai.ChatCompletion.create(model=GPT_MODEL, messages=messages, temperature=0)
    response_message = response["choices"][0]["message"]["content"]
    return {"answer": response_message}

if __name__ == "__main__":
    import os

    # Disable tokenizers parallelism
    os.environ["TOKENIZERS_PARALLELISM"] = "false"  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

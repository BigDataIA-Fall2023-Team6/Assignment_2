import requests
from io import BytesIO
import time
from pypdf import PdfReader
from transformers import GPT2TokenizerFast
from dotenv import load_dotenv
import os
import pandas as pd
import openai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy import spatial

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

def pdf_url_summary_nougat(pdf_url,ngrok_url):
    try:
        # Download the PDF file from the URL
        response = requests.get(pdf_url)
        response.raise_for_status()

        # Create a file-like object from the response content
        file_data = response.content

        # Prepare the file for uploading
        files = {'file': ('uploaded_file.pdf', file_data, 'application/pdf')}

        ng_url = ngrok_url

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

df = []


def generate_context_from_summary(summary: str): 
    sections = summary.split("\n") 
    filtered_sections = [section for section in sections if len(section.split()) > 15]

    if filtered_sections:
        
        data = {
            "text": filtered_sections
        }
        df = pd.DataFrame(data)
        context = "\n".join(filtered_sections)
        return context
    else:
        print("No filtered sections found in the summary.")
        return "Unable to extract text from the PDF"

def generate_context_from_summary_nougat(summary: str):
    # Split sections based on double newline characters
    sections = summary.split("\n") 
    
    # Filter sections that have more than 20 words (adjust as needed)
    filtered_sections = [section for section in sections if len(section.split()) > 15]

    if filtered_sections:
        data = {
            "text": filtered_sections
        }

        # Create a DataFrame for better visualization
        df = pd.DataFrame(data)

        print("Filtered Sections:")
        print(df)

        # Join the filtered sections to create context
        context = "\n".join(filtered_sections)

        return context
    else:
        print("No filtered sections found in the summary.")
        return "Unable to extract text from the PDF"

load_dotenv()
api_key = os.getenv('openapi_key') #Uncomment this and run the command.
openai.api_key = api_key

# nlp = spacy.load("en_core_web_md")

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

# def strings_ranked_by_relatedness(query, text, top_n=100):
#     query_embedding = nlp(query).vector
#     text_embeddings = [nlp(section).vector for section in text]
#     similarities = [cosine_similarity(query_embedding, embedding) for embedding in text_embeddings]

#     sorted_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)

#     top_strings = [text[i] for i in sorted_indices[:top_n]]
#     top_relatednesses = [similarities[i] for i in sorted_indices[:top_n]]

#     return top_strings, top_relatednesses


# def cosine_similarity(vector1, vector2):
#     dot_product = sum(a * b for a, b in zip(vector1, vector2))
#     magnitude1 = sum(a * a for a in vector1) ** 0.5
#     magnitude2 = sum(b * b for b in vector2) ** 0.5
#     if magnitude1 == 0 or magnitude2 == 0:
#         return 0
#     return dot_product / (magnitude1 * magnitude2)

EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"


def strings_ranked_by_relatedness(
    query: str,
    text: str,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 20
) -> tuple[list[str], list[float]]:
    
    try:
        query_embedding_response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=query,
        )
    except Exception as e:
        print(e)
        return ""
    
    query_embedding = query_embedding_response["data"][0]["embedding"]
    df = pd.DataFrame({"context":[]})
    df = pd.append({"context":text},ignore_index=True)
    text_embeddings = create_embedding(text)
    strings_and_relatednesses = [
        (df["context"], relatedness_fn(query_embedding, text_embeddings))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

def create_embedding(context):
    try:
        response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input= context
        )
        embeddings = [item['embedding'] for item in response['data']]
        flattened_embeddings = [value for sublist in embeddings for value in sublist]
        return flattened_embeddings  #np.array(flattened_embeddings).astype('float32')
    except Exception as e:
        print(f"Error in generating Embedding: {e}")
        return ""

## Generate Context Based ON OPEN AI EMBEDDING

# def generate_context_from_summary(summary: str):
 
#     sections = summary.split("\n") 
#     filtered_sections = [section for section in sections if len(section.split()) > 20]

#     if filtered_sections:      
#         data = {
#             "text": filtered_sections
#         }
#         df = pd.DataFrame(data)        

#         df['embedding']=df["text"].apply(create_embedding)

#         context = "\n".join(filtered_sections)
#         return context, df
#     else:
#         print("No filtered sections found in the summary.")
#         return "Unable to extract text from the PDF"

# def generate_context_from_summary(summary: str):
#     sections = summary.split("\n") 
#     filtered_sections = [section for section in sections if len(section.split()) > 20]

#     if not filtered_sections:
#         print("No filtered sections found in the summary.")
#         return "Unable to extract text from the PDF", pd.DataFrame()

#     data = {"text": filtered_sections}
#     df = pd.DataFrame(data)
#     # df['embedding'] = df["text"].apply(create_embedding)
#     # print(df['embedding'].head())

#     dimension = len(df['embedding'][0])
#     index = faiss.IndexFlatL2(dimension)
#     # embeddings_matrix = np.vstack(df['embedding'].values)

#     # Adding vectors to the index
#     embeddings_matrix = np.array(df['embedding'].tolist(), dtype=np.float32)
#     index.add(embeddings_matrix)

#     print(embeddings_matrix.shape)
#     print(embeddings_matrix.dtype)

#     # # Create a Faiss index
#     # index = faiss.IndexFlatL2(embeddings_matrix.shape[1])
#     # index.add(embeddings_matrix)

#     # print(df)
#     # max_length = df['embedding'].apply(len).max()
#     # print(max_length)
#     # index = faiss.IndexFlatL2(max_length)
#     # index.add(df['embedding'])

#     # Saving
#     with open("faiss_data1.pkl", "wb") as f:
#         pickle.dump(index, f)
    
#     context = "\n".join(filtered_sections)

#     return context, df



################################
# Generating Similarity
################################

# def strings_ranked_by_relatedness(query, text, top_n=20):

#     with open("faiss_data.pkl", "rb") as f:
#         index, df = pickle.load(f)

#     query_embedding = create_embedding(query).reshape(1, -1)
#     # df = pd.DataFrame.from_dict(text)
#     # Assuming the 'embedding' column of the df contains embeddings as lists

#     D, I = index.search(query_embedding, k=1)  # k=1 to get the most similar entry

#     # Return the most similar text from DataFrame
#     return df.iloc[I[0][0]]["text"]


#     # similarities = [cosine_similarity([query_embedding], [embedding])[0][0] for embedding in df['embedding']]
    
#     # sorted_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)
    
#     # top_strings = df['context'].iloc[sorted_indices[:top_n]].tolist()
#     # top_relatednesses = [similarities[i] for i in sorted_indices[:top_n]]
#     # return top_strings, top_relatednesses

#     # query_embedding = create_embedding(query)
#     # df = pd.DataFrame.from_dict(text)

#     # # text_embeddings = create_embedding(text)
#     # similarities = [query_embedding.similarity(embedding) for embedding in df['embedding']]
    
#     # # similarities = [cosine_similarity(np.vstack(query_embedding.to_list()), np.vstack(text_embeddings.to_list()))]
#     # sorted_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)
    
#     # top_strings = [text[i] for i in sorted_indices[:top_n]]
#     # top_relatednesses = [similarities[i] for i in sorted_indices[:top_n]]
#     # print(top_strings)
#     # return top_strings, top_relatednesses



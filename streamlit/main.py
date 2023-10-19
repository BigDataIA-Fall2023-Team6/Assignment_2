import streamlit as st
import requests
import pandas as pd
    
if 'context' not in st.session_state:
    st.session_state.context = ""


st.title("PDF to Text Converter & Chatbot")
global context
context = ""
# Input field for the PDF URL
conversion_choice = st.radio("Select a Conversion Library:", ["PyPDF2", "Nougat"])
pdf_url = st.text_input("Enter the URL of the PDF:")


if conversion_choice == "PyPDF2":
    if st.button("Convert to Text"):
        if pdf_url:
             
            # Call the PyPDF2 conversion function and display text and summary
            response = requests.post("http://127.0.0.1:8000/convert_pdf", json={"pdf_url": pdf_url, "library": "PyPDF2"})
            text = response.json()["text"]
            summary = response.json()["summary"]

            st.subheader("Extracted Text:")
            st.text(text)

            st.subheader("Summary:")
            st.write(summary)

            # Allow the user to set context and ask questions
            
            response = requests.post("http://127.0.0.1:8000/data-collection", json={"summary": text})
            context = response.json()["context"]
            st.session_state.context = context
            st.subheader("Context Set from Text Extraction")
            st.text(f"Context: {st.session_state.context}")   
            
        else:
            st.warning("Please enter a valid PDF URL.")

elif conversion_choice == "Nougat":
        st.subheader('Analyzing PDF using: Nougat')

        colab_link = "https://colab.research.google.com/drive/1be38KgK5yzhJYR5mmSLMhrNuQnLIs8P2"
        
        st.markdown(f"**To get an ngrok URL, click [here]({colab_link}) to open the Colab notebook.**")
        
        ngrok_url = st.text_input('Enter the ngrok url', '')
        st.write('The current URL is', ngrok_url)

        if st.button("Convert"):
            if pdf_url:
                # Call the conversion function and display the result for Nougat API              

                response = requests.post("http://127.0.0.1:8000/nougatconvert_pdf", json={"pdf_url": pdf_url, "ngrok_url": ngrok_url, "library": "NougatAPI"})
                text = response.json()["text"]

                # result = pdf_url_summary_nougat(pdf_url,ngrok_url)

                response = requests.post("http://127.0.0.1:8000/data-collection", json={"summary": text})
                context = response.json()["context"]
                st.session_state.context = context
                
                if text:
                    st.subheader("Nougat API Response:")
                    st.write(text)
                    st.write(f"Context: {st.session_state.context}") 
                else:
                    st.error("Failed to analyze the PDF using Nougat API.")
                
else:
        st.warning("Please select a conversion library.")
        
        
question = st.text_input("Enter a question:")
if st.button("Get Answer"):
    if question and st.session_state.context:
        st.text(f"Context: {st.session_state.context}")
        response = requests.post("http://127.0.0.1:8000/ask", json={"question": question, "context": context})
        answer = response.json()["answer"]
        # answer = get_answer(question, context)
        st.subheader("Answer:")
        st.write(answer)
             
    else:
            st.warning("Please enter a question.")    


# question = st.text_input("Enter a question:")
# @st.cache_data
# def get_answer(question, context):
#     print("Context:",context)
#     response = requests.post("http://127.0.0.1:8000/ask", json={"question": question, "context": context})
#     answer = response.json()["answer"]
#     return answer
# if st.button("Get Answer"):
#     if question:
    
#         # response = requests.post("http://127.0.0.1:8000/ask", json={"question": question, "context": context})
#         # answer = response.json()["answer"]
#         answer = get_answer(question, context)
#         st.subheader("Answer:")
#         st.write(answer)
#         st.text(f"Context: {context}")

#         # Send the question to the FastAPI endpoint
    
#     else:
#         st.warning("Please enter a question.")
    


# def get_answer(question, context):
#     if st.button("Get Answer"):
#         if question:
            
            
#             response = requests.post("http://127.0.0.1:8000/ask", json={"question": question, "context": context})
#             answer = response.json()["answer"]
#             return answer
#         else:
#             st.warning("Please enter a question.")

# Initialize context in session state





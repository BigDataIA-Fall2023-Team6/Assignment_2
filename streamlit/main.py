import streamlit as st
import time
from pypdfScanner import pypdf_url_summary
from nougatScanner import pdf_url_summary_nougat

def main():
    st.title("PDF to Text Converter")

    # Input field for the PDF URL
    pdf_url = st.text_input("Enter the URL of the PDF:")

    page_names = ['PyPDF','Nougat']
    page = st.radio('Select Library', page_names)

    if page =='PyPDF':
        st.subheader('Analysing PDF using: PyPDF')

        if st.button("Convert"):
            if pdf_url:
                # Call the conversion and summarization function
                text, summary = pypdf_url_summary(pdf_url)

                if text:
                    st.subheader("Extracted Text:")
                    st.text(text)

                    st.subheader("Summary:")
                    st.write(summary)
                else:
                    st.error("Unable to extract text from the PDF.")
            else:
                st.warning("Please enter a valid PDF URL.")


    if page =='Nougat':
# <<<<<<< FeatureBranch_Vivek
        st.subheader('Analyzing PDF using: Nougat')

        colab_link = "https://colab.research.google.com/drive/1be38KgK5yzhJYR5mmSLMhrNuQnLIs8P2"
        st.markdown(f"**To get an ngrok URL, click [here]({colab_link}) to open the Colab notebook.**")

        ngrok_url = st.text_input('Enter the ngrok url', '')
        st.write('The current URL is', ngrok_url)

        if st.button("Convert"):
            if pdf_url:
                # Call the conversion function and display the result for Nougat API
                              
                nstart_time=time.time()

                result = pdf_url_summary_nougat(pdf_url,ngrok_url)

                nend_time=time.time()
                computation_ntime= nend_time-nstart_time

                st.write("Time Taken for Nougat to Summarize:", computation_ntime)

                if result:
                    st.subheader("Nougat API Response:")
                    st.write(result)
                else:
                    st.error("Failed to analyze the PDF using Nougat API.")
            else:
                st.warning("Please enter a valid PDF URL.")

if __name__ == "__main__":
    main()
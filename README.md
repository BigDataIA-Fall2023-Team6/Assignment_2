# Assignment_2
OpenAI Chatbot on PDF Text Extraction

## Abstract 📝
In the era of digital information, the extraction of textual content from PDF documents for further analysis and interaction has become a pressing need. This project presents the design and development of a streamlit application, aimed at facilitating seamless PDF to text conversion. We have extracted text from the PDF using Nougat and PyPDF Library. To enhance the experience we have deployed FASTAPIs for smooth connection, enabling rapid and reliable interactions within the components of the application. Once the text is extracted from the PDF, users can pose questions related to the content, to which the OpenAI Chatbot provides pertinent answers. 

---

### Links 📎
*  Codelab Doc - [link]()
*  Streamlit Application - [link]()
*  Colab Notebook - [link]()
*  Datasets (SEC.gov) - [link](https://www.sec.gov/forms)

### Tools
* 🔧 Streamlit - [link](https://streamlit.io/)
* 🔧 NougatOCR - [link](https://github.com/facebookresearch/nougat)
* 🔧 PyPDF2 - [link](https://pypdf2.readthedocs.io/en/3.0.0/)
* 🔧 Google Colab - [link](https://colab.research.google.com/)
* 🔧 AWS s3 - [link](https://aws.amazon.com/s3/)
* 🔧 FastAPI - [link](https://github.com/tiangolo/fastapi)
* 🔧 Heroku - [link](https://devcenter.heroku.com/articles/getting-started-with-python)
* 🔧 OpenAI - [link](https://github.com/openai/openai-python)

---

## PDF to Text Extraction and OpenAI Chatbot

### Architecture 

![alt text]()


### Project Structure
```text
Assignment_2
├── CookBookForPDF
│   ├── OpenAIPDF.ipynb
│   ├── sec_pdfs_data.csv
│   ├── sec_pdfs_embb.csv
│   ├── sec_pdfs_qa.csv
├── architecture_diagram_generator.py
├── fastapi
│   ├── helper.py
│   ├── main.py
│   ├── Pipfile.txt
│   ├── Pipfile.lock
├── streamlit
│   ├── main.py
├── .envExample
├── README.md
└── requirements.txt
```

### Project Flow

1. User gives Http/Https PDF link to Streamlit App hosted on Streamlit Cloud
2. If the PDF Processor is PyPDF it processes the PDF on Streamlit Cloud itself
3. If the PDF Processor is Nougat it sends the downloaded PDF to Ngrok Agent, it forwards it to Google Colab ngrok service
4. Nougat API processes the PDF and returns the MMD file via HTTP to streamlit application
5. User downloads files from Streamlit and the Summary is displayed to the User
6. A context is created from the text generated from the PDF Processor and passed in the OpenAI
7. Created a prompt to answer the question asked by the user using the context created only
8. Answer is generated using OpenAI and displayed to the user

---

### Steps to execute Streamlit application
App can be directly accessed from Streamlit Cloud via [link]()

OR

1. Clone the [repository](https://github.com/BigDataIA-Fall2023-Team6/Assignment_2.git) to your local machine:
   ```
   git clone <repository_url>
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies from the `requirements.txt` file:
   ```
   pip install -r requirements.txt
   ```

4. Install the en_core_web_md module in Spacy to run the program.
   ```
   python -m spacy download en_core_web_md
   ```

5. Run the FastAPI application:
   ```
   cd fastapi/
   uvicorn main:app --reload --port 8000
   ```

6. Run the Streamlit application:
   ```
   streamlit run streamlit/main.py
   ```

7. Access the tool through your web browser at `http://localhost:8501`.

---

### Steps to execute NougatAPIServer on Google colab

1. Click the Google Colab Notebook [link](https://colab.research.google.com/drive/1be38KgK5yzhJYR5mmSLMhrNuQnLIs8P2)

2. Select 'T4 GPU' on colab runtime and run the cells. Please follow the instructions in cell comments.

3. Run All Cells

4. Note: Sometimes the connection is not established immediately when you run all cells. Execute the second last command with "public_url = ngrok.connect(port)" again.

5. Replace the public URL with your generated URL in the parameter "nougat_api_url" and check if the connectivity is successful

6. The colab notebook will generate a public URL to Nougat API server. Use that for your experimentation with either hosted streamlit app.

---

### Observations and Challenges

- When we limited the word counts to 40 to generated the context- No context was generated from the small pdfs using PyPDF.
- 

---

### Scope
We have created this tool to understand the basic PDF to Text conversation and implementation of OpenAI to generate answers based out of context based questions.

If you encounter any issues or have suggestions for improvements, please feel free to open an issue or contribute to this project. Your feedback is valuable in enhancing the tool's functionality and usability.

---
## Contribution
*   Abhishek : 33`%` 
*   Dilip : 33`%`
*   Vivek : 34`%`

## Team Members 👥
- Abhishek Sand
  - NUID 002752069
  - Email sand.a@northeastern.edu
- Dilip Sharma
  - NUID 
  - Email sharma.dil@northeastern.edu
- Vivek H
  - NUID 
  - Email 

## Individual Distribution

| **Developer** 	|          **Deliverables**          	|
|:-------------:	|:----------------------------------:	|
|      Abhishek    	| Open AI Cookbook Implementation       |
|      Abhishek    	| Git setup and integration             |
|      Abhishek    	| Nougat Fast APIs                      |
|      Vivek      	| Open AI Cookbook Implementation       |
|      Vivek      	| Fast APIs for Open AI                 |
|      Vivek      	| Fast APIs for PyPDF                   |
|      Dilip      	| Hosting on Heruku                    	|
|      Dilip      	| Architecture Diagrams                 |
|      Dilip      	| Fine-tuning the model                 |
|      Abhishek    	| Documentation                         |


---
---

> WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.
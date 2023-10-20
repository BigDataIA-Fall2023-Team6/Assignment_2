from diagrams import Diagram, Cluster
from diagrams.onprem.client import Users
from diagrams.aws.compute import LambdaFunction
from diagrams.aws.ml import Sagemaker
from diagrams.gcp.analytics import BigQuery
from diagrams.aws.storage import S3
from diagrams.onprem.compute import Server  # Add the Server component

# Define custom nodes for Nougat API
class NougatAPI(Server):
    def __init__(self, label):
        super().__init__(label)

# Define custom nodes for PyPDF
class PyPDF(LambdaFunction):
    def __init__(self, label):
        super().__init__(label)

# Define custom nodes for Data Collection
class DataCollection(LambdaFunction):
    def __init__(self, label):
        super().__init__(label)

# Define custom nodes for OpenAI
class OpenAI(LambdaFunction):
    def __init__(self, label):
        super().__init__(label)

# Define custom nodes for Streamlit
class Streamlit(Server):
    def __init__(self, label):
        super().__init__(label)

with Diagram("Streamlit Application Architecture", show=False):
    with Cluster("Users"):
        users = Users("Users")

    with Cluster("Question"):
        question = Users("User Question")
    
    with Cluster("Streamlit App"):
        streamlit_app = Streamlit("Streamlit App")
    
    with Cluster("Conversion Library"):
        conversion_library = Sagemaker("Select Library")
    
    with Cluster("PyPDF2 Library"):
        pypdf2 = PyPDF("PyPDF2")
    
    with Cluster("Nougat API (Google Colab)"):
        nougat_api = NougatAPI("Nougat API")
    
    with Cluster("Data Collection"):
        data_collection = DataCollection("Data Collection")
    
    with Cluster("OpenAI"):
        openai = OpenAI("OpenAI")
    
    with Cluster("Result"):
        summary = Streamlit("Result")

    users >> streamlit_app
    streamlit_app >> question
    streamlit_app >> conversion_library
    conversion_library >> pypdf2
    conversion_library >> nougat_api
    pypdf2 >> data_collection
    nougat_api >> data_collection
    data_collection >> openai
    question >> openai
    openai >> summary
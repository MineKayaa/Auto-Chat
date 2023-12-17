from operator import itemgetter
from flask import Flask,request , Blueprint
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings  import VertexAIEmbeddings
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.llms import VertexAI
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.prompts  import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.chains import RetrievalQA  


chatbot_Blueprint = Blueprint('chatbot', __name__)



@chatbot_Blueprint.route("/chatbot",methods=['GET'])
def chain():
    args = request.args
    input = args.get("input")

    documents = documentProcessor()
    vectorstore = Chroma.from_documents(documents=documents, 
                                     embedding = VertexAIEmbeddings())
    
    
    retriever = vectorstore.as_retriever(search_type="mmr")

    llm = VertexAI(model_name="text-bison@001")
    
    chain=mainChain(retriever,llm)
    answer=chain.invoke({"question":str(input),"language":"turkish"})
   
    return answer


def mainChain(retriver,llm):
    template = """
        You are a chatbot that will help users get the necessary maintenance done on their cars.
        You have information about the brand, model, owner of the car also there is information about the maintenance done on the cars so far.
        Maintenances have min_km information. This means that if a car pass this km , it should undergo to related maintenances.
        They will ask you question about what type of maintenances need for their car.
        You have where they can find the services , give recommendation based on user city, don't forget it is important to know car's brand if there is no service for that brand, say there is no service for that brand and give another city recommendation.
        If you couldn't find the answer in the context, just say that you don't know, don't try to make up an answer. 
        Always give kind answers. 
        Answer the question based on the following context:  
        {context}

        Question: {question}

        Answer in the following language: {language}
        """
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {
            "context": itemgetter("question") | retriver,
            "question": itemgetter("question"),
            "language":itemgetter("language"),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def loader():
    loader_services = CSVLoader(file_path='files/services.csv', csv_args={
                                                                 'delimiter': ',',
                                                                 'quotechar': '"',
                                                                 'fieldnames': ['service_name', 'address', 'city', 'telefon_no'] })
    loader_main_type = CSVLoader(file_path='files/maintenece-types.csv', csv_args={
                                                                'delimiter': ',',
                                                                'quotechar': '"',
                                                                'fieldnames': ['bakim_tipi', 'min_km'] })
    loader = CSVLoader(file_path='files/car-history-with-user.csv', csv_args={
                                                                'delimiter': ',',
                                                                'quotechar': '"',
                                                                'fieldnames': ['car_id', 'marka', 'model', 'kullanici', 'bakim_tipi', 'tarih', 'service_name'] })
    data = loader.load() + loader_main_type.load() 
    #print(data)
    return data


def documentProcessor():
    data = loader()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, length_function = lambda x: len(x.split("\n")))
    splits = text_splitter.split_documents(data)
    return splits

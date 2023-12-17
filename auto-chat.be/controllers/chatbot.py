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
    
    
    #takes k doc result with above 0.5 similarity score
    retriever = vectorstore.as_retriever()
                               # search_type="similarity_score_threshold", 
                               # search_kwargs={"score_threshold": .5 , 
                               #                "k": 8})


    llm = VertexAI(model_name="text-bison@001")
    
    chain=mainChain(retriever,llm)
    answer=chain.invoke({"question":str(input),"language":"turkish"})
   
    return answer


def mainChain(retriver,llm):
    template = """
        You are a chatbot that will help users get the necessary maintenance done on their cars.
        You have information about the brand, model, owner of the car, and mileage of their cars (km). you can search on metadata=.source = car-user.csv
        There is information about the maintenance done on the cars so far. you can search on metadata.source = car-history.csv
        Maintenances also have min - max km information, for example, if the car has 15,000 km, all maintenance with min_km less than 15,000 must be done.
        For example, if the car has 20,000 km, it must have undergone maintenance twice with a min_km of 10,000. metadata.source = maintenece-types.csv
        They will ask you question about what type of maintenances need for their car.
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
    loader = CSVLoader(file_path='files/car-history.csv', csv_args={
                                                                'delimiter': ',',
                                                                'quotechar': '"',
                                                                'fieldnames': ['car_id', 'bakım_tipi', 'tarih'] })
    loader_main_type = CSVLoader(file_path='files/maintenece-types.csv', csv_args={
                                                                'delimiter': ',',
                                                                'quotechar': '"',
                                                                'fieldnames': ['bakım_tipi', 'min_km', 'max_km'] })
    loader_user = CSVLoader(file_path='files/car-user.csv', csv_args={
                                                                'delimiter': ',',
                                                                'quotechar': '"',
                                                                'fieldnames': ['car_id', 'marka', 'model', 'kullanıcı', 'araba_km'] })
    data = loader.load() + loader_main_type.load() + loader_user.load()
    #print(data)
    return data


def documentProcessor():
    data = loader()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0, length_function = lambda x: len(x.split("\n")))
    splits = text_splitter.split_documents(data)
    #print(splits)
    return splits

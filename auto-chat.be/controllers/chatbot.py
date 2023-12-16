from flask import Flask,request , Blueprint
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings  import VertexAIEmbeddings
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.llms import VertexAI
from langchain.document_loaders.csv_loader import CSVLoader


chatbot_Blueprint = Blueprint('chatbot', __name__)



@chatbot_Blueprint.route("/chatbot",methods=['GET'])
def chain():
    args = request.args
    input = args.get("input")

    
    loader = CSVLoader(file_path='files/car-history.csv')
    loader_main = CSVLoader(file_path='files/car-maintenance.csv')
    loader_main_type = CSVLoader(file_path='files/maintenece-types.csv')
    data = loader.load() + loader_main.load() + loader_main_type.load()


    print(data)
   
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    splits = text_splitter.split_documents(data)

    vectorstore = Chroma.from_documents(documents=splits, 
                                    embedding = VertexAIEmbeddings())
    #takes k doc result with above 0.5 similarity score
    retriever = vectorstore.as_retriever(
                                search_type="similarity_score_threshold", 
                                search_kwargs={"score_threshold": .5 , 
                                               "k": 5})
    

    

    llm = VertexAI(model_name="text-bison@001")

    memory = ConversationSummaryMemory(
        llm=llm, memory_key="chat_history", return_messages=True
    )

    assistant = ConversationalRetrievalChain.from_llm(llm=llm, 
                                           retriever=retriever, 
                                           memory=memory)

    
    result = assistant(input)
    answer = result["answer"]
  
    return answer


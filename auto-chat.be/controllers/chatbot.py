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


chatbot_Blueprint = Blueprint('chatbot', __name__)



@chatbot_Blueprint.route("/chatbot",methods=['GET'])
def chain():
    args = request.args
    input = args.get("input")

    documents = documentProcessor()

    vectorstore = Chroma.from_documents(documents=documents, 
                                    embedding = VertexAIEmbeddings())

    #takes k doc result with above 0.5 similarity score
    retriever = vectorstore.as_retriever(
                                search_type="similarity_score_threshold", 
                                search_kwargs={"score_threshold": .5 , 
                                               "k": 8})
    

    llm = VertexAI(model_name="text-bison@001")

    # memory = ConversationSummaryMemory(
    #     llm=llm, memory_key="chat_history", return_messages=True
    # )

    # assistant = ConversationalRetrievalChain.from_llm(llm=llm, 
    #                                        retriever=retriever, 
    #                                        memory=memory)

        
    # result = assistant(input)
    # answer = result["answer"]
  
    chain=mainChain(retriever,llm)
    answer=chain.invoke({"question":str(input),"language":"english"})
   
    return answer


def mainChain(retriver,llm):
    template = """
        You are a chatbot for data you have, Data contains information about cars and operations happened on them.
        maintenance_type is a operation type happened on car, there is historical information about this opeartions, you can find who has the car with a user_id. 
        I will give you the context related to the question, except this context as a ground truth.
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
    loader = CSVLoader(file_path='files/car-history.csv')
    loader_main = CSVLoader(file_path='files/car-maintenance.csv')
    loader_main_type = CSVLoader(file_path='files/maintenece-types.csv')
    loader_user = CSVLoader(file_path='files/car-user.csv')
    data = loader.load() + loader_main.load() + loader_main_type.load() + loader_user.load()
    #print(data)
    return data


def documentProcessor():
    data = loader()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    splits = text_splitter.split_documents(data)
    return splits

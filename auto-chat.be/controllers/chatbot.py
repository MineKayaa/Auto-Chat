from flask import Flask,request , Blueprint
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings  import VertexAIEmbeddings
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from langchain.llms import VertexAI


chatbot_Blueprint = Blueprint('chatbot', __name__)

embeddings =  VertexAIEmbeddings()

@chatbot_Blueprint.route("/chatbot",methods=['GET'])
def chain():
    args = request.args
    input = args.get("input")

    docs = "s"
   
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    splits = text_splitter.split_documents(docs)

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


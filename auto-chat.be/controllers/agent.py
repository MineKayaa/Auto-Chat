from flask import Flask,request , Blueprint
import pandas as pd
import tabulate
from langchain.llms import VertexAI

from langchain.chat_models import ChatOpenAI

from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.agents.agent_types import AgentType


agent_Blueprint = Blueprint('agent', __name__)

OPENAI_API_KEY = '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'

car_history_path = "files/car-history.csv"
car_user_path = "files/car-user.csv"
maintenance_type_path = "files/maintenece-types.csv"

llm= ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

llm_vertex= VertexAI(model_name="text-bison@001")

@agent_Blueprint.route("/agent",methods=['GET'])
def chain():
    args = request.args
    input = args.get("input")

    agent = create_csv_agent(
        llm,
        [car_history_path, car_user_path, maintenance_type_path ], 
        verbose=True,
        handle_parsing_errors=True,
        stop=["\nObservation:"],
        agent_type=AgentType.OPENAI_FUNCTIONS
    )

    prompt = (
        """ You are a chatbot that will help users get the necessary maintenance done on their cars.
        You have information about the brand, model, owner of the car, and mileage of their cars (km). you can search on df2
        There is information about the maintenance done on the cars so far. you can search on df1
        Maintenances also have min - max km information, for example, if the car has 15,000 km, all maintenance with min_km less than 15,000 must be done.
        For example, if the car has 20,000 km, it must have undergone maintenance twice with a min_km of 10,000. you can search on df3
        They will ask you question about what type of maintenances need for their car.
            I will give you information about where to find data on df's below.
            
            Give responses to the question on the end of the text :
          
            df1 contains data about the operations the cars undergo, its like history of operations happened on car. 
            You can find car's brand and model information on df2, search for car_id.
            df1 columns and column descriptions as following:
            car_id: id of the car
            bakım_tipi: type of a operation happened on car
            tarih : date of the operation 

            df2 contains data about who has the car and car's brand, model and km information. 
            On df1 you can find, car's operation history. df1's car_id and df2's car_id is same.
            df2 columns and column descriptions as following:
            car_id: id of the car
            marka: brand of the car
            model: model of the car
            kullanıcı : name of the user who has the car
            araba_km : km of the car

            df3 contains data about the operations. Operatation is bakım_tipi 
            df4's maintenance_type, df2's maintenance_type and  df4's maintenance_type are same.
            df4 columns and column descriptions as following:
            bakım_tipi: type of a operation 
            min_km : min km for the operation 
            max_km : max km for the operation 


            
            Below is the question
            Question:
           
            """
       + input
        
    )


    answer = agent.run(prompt)
  
    print(answer)
    return answer


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
car_maintenance_path = "files/car-maintenance.csv"
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
        [car_history_path, car_maintenance_path, car_user_path, maintenance_type_path ], 
        verbose=True,
        handle_parsing_errors=True,
        stop=["\nObservation:"],
        agent_type=AgentType.OPENAI_FUNCTIONS
    )

    prompt = (
        """ You are a question-answering bot over the data you queried from dataframes.
            I will give you information about where to find data on df's below.
            
            Give responses to the question on the end of the text :
          
            df1 contains data about the operations the cars undergo, its like history of operations happened on car. 
            Operatation is maintenance_type , you can find maintenance name on df4. 
            df1's maintenance_type and df4's maintenance_type are same, you can check for name on df4.
            You can find car's brand and model information on df3, search for car_id.
            df1 columns and column descriptions as following:
            car_id: id of the car
            maintenance_type: type of a operation happened on car
            date : date of the operation 
            user_id : id of the user who has the car

            df2 contains data about the operations the cars has to have on spesific period. 
            Period are represents months , for example if a car has a 3 period for spesific maintenance_type, this means that the car has to have this operation once in 3 months.
            Operatation is maintenance_type , you can find maintenance name on df4. 
            df2's maintenance_type and df4's maintenance_type are same, you can check for name on df4.
            df2 columns and column descriptions as following:
            car_brand: brand of the car
            car_model: model of the car
            maintenance_type: type of a operation should happened on car
            period : How often will maintenance take place

            df3 contains data about who has the car and car's brand and model information. 
            On df1 you can find, car's operation history. df1's car_id and df3's car_id is same.
            df3 columns and column descriptions as following:
            car_id: id of the car
            car_brand: brand of the car
            car_model: model of the car
            user_id : id of the user who has the car

            df4 contains data about the operations. Operatation is maintenance_type 
            df4's maintenance_type, df2's maintenance_type and  df4's maintenance_type are same.
            df4 columns and column descriptions as following:
            maintenance_type: type of a operation 
            maintenance_type : name of the operation 


            
            Below is the question
            Question:
           
            """
       + input
        
    )


    answer = agent.run(prompt)
  
    print(answer)
    return answer


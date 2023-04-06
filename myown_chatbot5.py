import os
from flask import Flask, request, Blueprint, jsonify
from flask_cors import CORS
from rasa.core.agent import Agent

from feature.Model import train_chatbot, save_rasa_dataset, predict_answer
from feature.Chatbot import ChatbotDataLoader, UserDataLoader, create_answer
from feature.Answer import Answer, load_answer, save_answer, updata_entity_contents

app = Flask(__name__)
CORS(app)

agent_dict = {"800":Agent.load('./bots/800/model/model.tar.gz')}

@app.route('/', methods=['GET'])
def main():
    return jsonify({'states':'ok'})


chat = Blueprint('chat',__name__, url_prefix='/chat')

@chat.route("/",methods=['GET'])
def health():
    return jsonify({'states':'ok'})

@chat.route("/dialog", methods=['POST'])
def dialog_connect():

    user_data = request.get_json()
    userData = UserDataLoader(user_data)

    userData.create_response(agent_dict.get(userData.bot_id))
    userData.update_dialogflow()

    ############ 테스트 코드
    response_data = [{"bot": userData.metadata['bot'], "user":userData.user,"dialogFlow":userData.dialogflow, "contents":userData.contents_list, "code":userData.code}]
    return jsonify(response_data)
    ############


@chat.route("/deploy", methods=['POST'])
def make_chatbot():
    json_data = request.get_json()
    chatbotData = ChatbotDataLoader(json_data)
    os.makedirs(chatbotData.response_file_path,exist_ok=True)
    os.makedirs(chatbotData.intent_model_path, exist_ok=True)

    chatbotData.save_response()
    chatbotData.save_metadata()

    if chatbotData.origin_id:
        chatbotData.update_origin_metadata()
    
    if chatbotData.use_model:
        chatbotData.train_intent_model()
        agent_dict.update({str(chatbotData.id) : Agent.load(chatbotData.intent_model_path + '/model.tar.gz')})
    return 'done'

@chat.route("/delete/<chatbot_id>", methods=['DELETE'])
def remove_chatbot(chatbot_id):
    from shutil import rmtree
    rmtree(f'./bots/{chatbot_id}')
    return 'done'


if __name__ == "__main__":
    app.register_blueprint(chat)
    app.debug = True
    app.run("0.0.0.0", port=5005, threaded=True)
'''
모듈설명 : 챗봇에 필요한 AI 모델 학습, 예측 모듈
작성자 : 허윤성
버전 : 1.0.0
생성일자 : 2022.07.26
최종수정일자 : 2022.07.26
최종수정자 : 허윤성
최종수정내용 : 최초생성
참조 파일 구성 : 
참조파일 위치 : 
'''
from feature.Util import force_sync

@force_sync
async def predict_answer(agent, text):
    
    '''
    모델 예측
    
    Parameters
    ----------
    text : str
        utterance for classification
        
    Returns
    ----------
    dict
        intent, entity dictionary
    '''

    result = await agent.parse_message(text)
    intent = result['intent']['name'] if result['intent']['confidence'] > 0.9 else None
    
    return {'intent': intent}

def train_chatbot(data_path, model_dir, config_file='config.yml'):
    
    '''
    model train function
    
    Parameters
    ----------
    data_json : str , file_path
        rasa train data format
        
    config_file : str , file_path
        spacy model config(yml)
        
    model_dir : str , model_save_path
        model dir
    '''
   
    from rasa.model_training import train_nlu

    train_nlu(config_file, data_path, model_dir ,fixed_model_name='model')
    
def save_rasa_dataset(meta_utterances, file_path):
    
    import json
    
    '''
    metadata utterance transform rasa data
    
    Parameters
    ----------
    meta_utterances : list
        metadata utterance data format
        
    file_path : str
        data dir
    '''
    
    if len(meta_utterances) == 1:
        meta_utteransces['empty'] = ['.']
    rasa_dataset = {}
    rasa_dataset['rasa_nlu_data'] = {}
    
    utter_list = []
    for intent, texts in meta_utterances.items():
        for text in texts:
            utter_list.append({'text':text, 'intent':str(intent), 'entities':[]})
    rasa_dataset['rasa_nlu_data']['common_examples'] = utter_list
    
    with open(file_path, 'w') as f:
            json.dump(rasa_dataset, f, indent=4)
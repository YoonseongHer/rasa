'''
모듈설명 : 1. 챗봇 API 구성, json data에서 원하는 데이터 발라내기
           2. 답변 로드 및 전송
작성자 : 허윤성
버전 : 1.0.1
생성일자 : 2023.03.06
최종수정일자 : 2023.03.06
최종수정자 : 허윤성
최종수정내용 : 최초생성
참조 파일 구성 : 
참조파일 위치 : 
'''
import nest_asyncio

from feature.Answer import Answer, save_answer, load_answer, updata_entity_contents
from feature.Model import train_chatbot, save_rasa_dataset, predict_answer
# from feature.TextPreprocessing import text_preprocessing

class ChatbotDataLoader():
    '''
    봇빌더 json data를 이용하여 챗봇 데이터 생성 class
    '''
    def __init__(self, json_data):
        '''
        빌더에서 보낸 chatbot info에서 필요한 데이터 발라내기
        
        Parameters
        ----------
        json_data : json
            빌더에서 받은 데이터
        '''
        self.json_data = json_data
        self.id = self.json_data['bot']['id']
        self.version = self.json_data['bot']['version']
        self.origin_id = self.json_data['bot']['originId']
        self.use_model = self.json_data['bot']['aiModel']
        self.blocks_origin = sum([snr['blocks'] for snr in self.json_data['scenarios']],[])
        self.userUtterance = {block['id']:[utter['name'] for utter in block['utterances']] for block in self.blocks_origin if block['utterances']}
        
        self.blocks = [(str(responses['id']),sorted(responses['responses'], 
                                 key=lambda x:(x['sequence'], x['order'])), responses['keywords']) for responses in self.blocks_origin]
        
        self.chatbot_path = f'./bots/{self.id}/'
        self.response_file_path = self.chatbot_path + 'response/'
        self.intent_model_path = self.chatbot_path + 'model/'
        self.origin_bot_path = f'./bots/{self.origin_id}/'
        
    def save_metadata(self):
        import json
        '''
        create meta data
        '''
        self.metadata = {}
        self.metadata['bot'] = {'id':self.id, 
                                'version':self.version, 
                                'originId' : self.origin_id,
                                'chatAvailable':self.use_model,
                                # 'name':self.json_data['bot']['name'],
                                'name' : self.json_data['bot']['profileName'],
                                # 'profileImgID' : self.json_data['bot']['profileImgId'],
                                'profile' : self.json_data['bot']['profileImgUrl']}
        
        self.metadata['chat'] = {'welcomeResponse' : [block['id'] for block in self.blocks_origin if block['blockType']=='welcome'][0],
                                 'fallbackResponse' : [block['id'] for block in self.blocks_origin if block['blockType']=='fallback'][0]}
        self.metadata['userUtterance'] = self.userUtterance
        self.metadata['path'] = {'responce':self.response_file_path, 'model':self.intent_model_path}
        
        with open(self.chatbot_path+'metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=4)
            
    def update_origin_metadata(self):
        import json
        
        with open(self.origin_bot_path+'metadata.json', "r") as json_file:
            origin_metadata = json.load(json_file)
            
        origin_metadata['bot']['current_id'] = self.id
        origin_metadata['bot']['version'] = self.version
            
        with open(self.origin_bot_path+'metadata.json', 'w') as f:
            json.dump(origin_metadata, f, indent=4)
            
    def save_response(self):
        '''
        save responses
        '''
        for block_id, block_responses, block_keywords in self.blocks:

            total_response = []
            seq_response = []
            answer_entity = []
            sequence = 1
            for response in block_responses:
                res_sequence = response['sequence']

                if sequence != res_sequence:
                    total_response.append(seq_response)
                    seq_response = []

                answer = Answer()
                create_answer(answer, response)
                seq_response.append(answer.return_answer())

                # extract
                extract_entity = [{'name':keyword['name'],'type':keyword['entity'], "essential":keyword['isRequired']} for keyword in block_keywords]
                # answer_entity
                entity_list = answer.answer_entitys()
                
                if entity_list:
                    answer_entity.append((len(total_response), len(seq_response)-1,entity_list))

                total_response.append(seq_response)
                answer_data = {'entity_info':{'extract':extract_entity, 'answer':answer_entity}, 'contents':total_response}
                save_answer(self.response_file_path, block_id, answer_data)
            
    def train_intent_model(self):
        '''
        train intent classification model
        '''
        save_rasa_dataset(self.userUtterance, self.intent_model_path+'train_data.json')
        train_chatbot(self.intent_model_path+'train_data.json', model_dir = self.intent_model_path)
        
class UserDataLoader():
    '''
    사용자 json data에서 원하는 값을 가져오는 class
    entity 추출
    '''
    def __init__(self, user_response_data):
        '''
        빌더에서 보낸 chatbot info에서 필요한 데이터 발라내기
        
        Parameters
        ----------
        json_data : json
            사용자에서 받은 요청 json data
        '''
        import json
        
        self.data = user_response_data
        self.bot = self.data['bot']
        self.bot_id = self.bot['id']
        # self.version = self.bot['version']
        self.origin_bot_path = f'./bots/{self.bot_id}/'
        
        with open(self.origin_bot_path+'metadata.json', "r") as json_file:
            self.metadata = json.load(json_file)
            
        self.chatbot_path = f"./bots/{self.metadata['bot'].get('current_id',self.bot_id)}/"
        # self.chatbot_path = f'./{self.bot_id}/'
        self.response_file_path = self.chatbot_path + 'response/'
        self.intent_model_path = self.chatbot_path + 'model/'
        self.userRequest = self.data['userRequest']
        self.user = self.userRequest['user']
        self.user_id = self.user['id']
        self.user_type = self.user['type']
        self.dialogflow = self.data['dialogFlow']
        self.dialog_history = self.dialogflow.get('history',[])
        self.situation = self.dialogflow.get('situation',{'status':'normal'})
        self.entitys = {x['name']:x['value'] for x in self.dialog_history[-1].get('entitys',[])} if self.dialog_history else {}
        self.input = self.dialogflow['userInput']
        self.input_type = self.input['type']
        self.input_value = self.input['value']
        if self.input_type == 'BUTTON':
            self.response = self.input_value[0].get('block','S100')
        elif self.input_type == 'CHAT':
            self.response = 'S900'
        self.extracted_entitys = {}
        
        with open(self.chatbot_path+'metadata.json', "r") as json_file:
            self.metadata = json.load(json_file)

    #-------------intent classfication-------------#
    
    def create_response(self, agent=''):
        
        # 메인 답변
        if self.situation['status'] == 'normal':
            input_type = self.input_type

            if input_type == 'BUTTON':
                intent = 'button'
                if self.input_value[0].get('type','') in ['URL', 'TEL']:
                    response_number = self.metadata['chat']['welcomeResponse']
                    self.code='DONE'
                else:
                    response_number = self.input_value[0].get('block','S100')
                    self.code = 'SUCCESS'
                
            elif input_type == 'CHAT':
                
                intent = next((key for key, lst in self.metadata['userUtterance'].items() if self.input_value[0] in lst), None)
                if agent:
                    intent = predict_answer(agent, self.input_value[0])['intent'] if not intent else intent
                else :
                    intent = self.metadata['chat']['fallbackResponse']
                # intent = None 일때 탈출블록 연결 필요
                response_number = intent if intent else self.metadata['chat']['fallbackResponse']
                self.code = 'SUCCESS'
                
            elif input_type=='':
                response_number = self.metadata['chat']['welcomeResponse']
                self.code = 'SUCCESS'
                
        elif self.situation['status'] == 'request':
            response_number = self.situation['block_id']
            
        answer = load_answer(self.response_file_path, str(response_number))
        extract_entity = answer['entity_info']['extract']
        replace_entity = answer['entity_info']['answer']
        contents_list = answer['contents']
        
        # entity 추출
        if self.situation['status'] == 'normal':
            extract_entity_list = extract_entity
                    
        elif self.situation['status'] == 'request':
            extract_entity_list = [self.situation['entity']]
            self.extracted_entitys = self.situation['extracted_entity']

        self.extract_entitys(extract_entity_list)
        self.required_entity = self.entity_check(extract_entity)
        
        if self.required_entity:
            answer = load_answer(response_file_path, self.required_entity['name'])
            contents_list = answer['contents']

        else:
            updata_entity_contents(contents_list, replace_entity, self.entitys)
        
        self.response = response_number
        self.contents_list = contents_list
    
    #-------------entity extract-------------------#    
    def entity_answer_count(self, entity_name):
        '''
        entity sys.answer.count 의 값을 추출하는 함수
        
        Parameters
        ----------
        entity_name : str
            봇빌더에서 설정한 entity name
        '''
        self.extracted_entitys[entity_name] = str(len(self.input_value))
        self.entitys.update(self.extracted_entitys)
        
    def extract_entitys(self, extract_entity_list):
        '''
        추출해야할 entity 를 모두 추출
        
        Parameters
        ----------
        extract_entity_list : list
            entity name, type info
        '''
        for entity in extract_entity_list:
            if entity['type'] == 'sys.answer.count':
                self.entity_answer_count(entity['name'])
    
    #-------------entity check-------------------#
    def entity_check(self, extract_list):
        '''
        추출된 entity 확인
        
        Parameters
        ----------
        extract_list :  list 
            each response answer extracted entity list
        '''
        for item in extract_list:
            if item['essential'] and not bool(self.extracted_entitys.get(item['name'],'')):
                return item
        return {}
    #-------------dialogFlow update-------------------#
    def update_dialogflow(self):
        if self.required_entity:
            self.dialogflow['situation'] = { 'status':'request',
                                        'block_id': self.response,
                                        'entity': self.required_entity, 
                                        'extracted_entity':self.extracted_entitys}
        else: 
            self.dialogflow['situation'] = {'status':'normal'}
            self.dialog_history.append({'intent': self.response, 'answer':[self.response], 'entitys':[{'name':key,'value':value} for key, value in self.entitys.items()]})
            self.dialogflow['history'] = self.dialog_history
            
def create_answer(answer, response):
    '''
    빌더 response 데이터 기반으로 Answer class에 답변을 만든다.
    
    Parameters
    ----------
    answer : class 
        Answer module Answer class
    
    response : dictionary
        answer dictionary in responses in blocks
    '''
    res_type = response['responseType'].split('_')
    main_type, btn_types = res_type[0], res_type[1:]
    
    if main_type == 'TEXT':
        text = response['content']
        answer.Text(text)
        
    elif main_type == 'IMAGE':
        image_url = response['imageUrl']
        answer.Image(image_url=image_url)
        
    elif main_type == 'CARD':
        title = response['title']
        image_url = response['imageUrl']
        description = response['desc']
        answer.Card(title=title, image_url=image_url, description=description)
        
    elif main_type == 'LIST':
        title_text = response['subject']
        title_img_url = response['imageUrl']
        
        list_items = [{"subject":lst['subject'],"desc": lst['desc'],"imageUrl":lst['imageUrl'],"link":lst['linkUrl']} for lst in response['list']]
        answer.List(title_text=title_text, image_url=title_img_url, item_list=list_items)
        
    if main_type == 'SLIDE':
        response_id = response['id']
        answer.Slide(response_id)
        
    if btn_types:
        res_buttons = sorted(response['buttons'], key=lambda x:x['order'])
        btn_type, select_type = btn_types
        btn_items = [{'type':btn['buttonType'],'label':btn['name'],'value':btn['functionalValue'],'order':btn['order']} for btn in res_buttons]
        for item in btn_items:
            print()
            if item['type'] in ['block','upload']:
                item['value'], item['block'] = item['order'], item['value']
            
            type_converter = {'block':'BLOCK',
                              'phone':'TEL',
                              'url' :'URL',
                              'upload':'IMAGE_UPLOAD'} 
        
            item['type'] = type_converter.get(item['type'], item['type'])
                
        answer.Button(btn_type=btn_type, select_type=select_type, buttons=btn_items)
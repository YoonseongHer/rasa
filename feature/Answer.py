'''
모듈설명 : 1. 챗봇의 답변 내용을 Json형식으로 생성, 수정, 저장
           2. 답변 번호를 이용하여 contents load
작성자 : 허윤성
버전 : 1.0.1
생성일자 : 2022.06.20
최종수정일자 : 2023.03.20
최종수정자 : 허윤성
최종수정내용 : Answer.return_answer , updata_entity_contents : data 구조 변경으로 인한 수정
참조 파일 구성 : 
참조파일 위치 : 
'''
import json

class Answer():
    '''
    각 답변의 유형에 맞게 json 형태 data 출력
    '''
    def __init__(self):
        '''
        content reset
        '''
        self.content = {'chatType':"TEXT",'chatData':{}}
        self.button = {'useButton':False}
        
    def Text(self,text):
        '''
        answer type Text create
        
        Parameters
        ----------
        text : str
            main text of answer
        '''
        self.__init__()
        self.content['chatType'] = 'TEXT'
        self.content["chatData"]["chatText"] = text
        
    def Image(self, image_url):
        '''
        answer type Image create
        
        Parameters
        ----------
        somenail_image_url : str
            answer image url
            
        origin_image_url : str
            origin image url to open when clik to open image
        '''
        self.__init__()
        self.content['chatType'] = 'IMAGE'
        self.content["chatData"] = {"imageUrl":image_url}
        
    def Card(self, image_url, title, description="",image_type='WIDE'):
        '''
        answer type Card create
         
        Parameters
        ----------
        image_url : str
            answer image url
        
        title : str
            card title
            
        description : str
            card main text
        '''
        self.__init__()
        self.content['chatType'] = 'CARD'
        card_item = { "imageUrl": image_url,
                      "title": title,
                      "description": description,
                      "leftButtonText": "",
                      "rightButtonText": ""}
        
        self.content["chatData"] = {"cardImageType":image_url,'cardItem': card_item}
        
    def List(self, title_text, image_url, item_list):
        '''
        answer type Card create
         
        Parameters
        ----------
        title_text : str
            list title text
            
        image_url : str
            list title image url
            
        item_list : list of dict value all str
                    [
                        {
                            "subject": "list item title", 
                            "desc": "list item description",
                            "imageUrl": "list item image URL",
                            "link": "list item link"
                        }
                    ]

        '''
        self.__init__()
        self.content['chatType'] = 'LIST'
        self.content['chatData'] = {"listTitle":title_text,"titleImageUrl":image_url, "listItem":item_list}
        
    def Slide(self, response_id):
        '''
        answer type Slide create
        
        Parameters
        ----------
        response_id : str
            response id in cell
        '''
        self.__init__()
        self.content['chatType'] = 'SLIDE'
        self.content['chatData'] = {"responseId":response_id}
    
    def Button(self, btn_type, select_type, buttons=[]):
        '''
        create button
        
        Parameters
        ----------
        btn_type : str 'VERTICAL','HORIZENTAL','DROPDOWN'
            
        buttons : list of dictionary value all str
            {
                "type"  : "button function type",
                "label" : "button label",
                "value" : "button function value"
                "order" : ""
            }
        '''
        
        self.button['useButton'] = True
        self.button['buttonData'] = {
            "buttonType": btn_type,
            "selectType": select_type,
            "buttonItem": buttons
        }
    
    def return_answer(self):
        '''
        return content with button
        
        Return
        ----------
        content : json
            asnwer with json form
        '''
        # self.content['button'] = self.button
        self.content.update(self.button)
        
        content = {"chatSubject" : "BOT", "data" : self.content}
        return content
    
    def answer_entitys(self):
        import re
        text = str(self.return_answer())
        text = text.replace(' ','')
        p = re.compile('{{[^{}]+}}')
        return [entity[2:-2] for entity in p.findall(text)]

    def save(self, file_path):
        with open(file_path, 'w') as f:
            json.dump([self.return_answer()], f, indent=4)
            
def save_answer(file_path, block_id, responses):
    '''
    답변 번호를 입력받아 파일의 contents로 변환
    
    Parameters
    ----------
    file_path : str
        response file path
        
    block_id: str
        response block id
    
    responses : list
        response list , Answer class retuen_answer
    
    returns
    ----------
    answer_list : list of contents(json)
        answer contents from file
    '''
    with open(file_path+block_id+'.json', 'w') as f:
            json.dump(responses, f, indent=4)
            
def load_answer(file_path, block_id):
    '''
    답변 번호를 입력받아 파일의 contents로 변환
    
    Parameters
    ----------
    file_path : str
        response file path
        
    block_id: str
        response block id
    
    returns
    ----------
    answer_list : list of contents(json)
        answer contents from file
    '''
    file_path = f'{file_path}'+block_id+'.json'

    with open(file_path, "r") as json_file:
        json_data = json.load(json_file)

    return json_data

def updata_entity_contents(contents, answer_entity_list, entity_dict):
    import re
    '''
    답변에 키워드(entity) 자리를 추출한 값으로 바꿔주는 함수
    
    Parameters
    ----------
    contents : list of list
        chatbot answer contents
        
    answer_entity_list: list of (x,y,[entity_name])
        entity location info
    
    entity_dict : dict
        replace entitiy dict
    
    returns
    ----------
    answer_list : list of contents(json)
        answer contents from file
    
    '''
    for x,y,entitys in answer_entity_list:
        content = contents[x][y]['data']
        content_type, content_data = content['chatType'], content['chatData']
        
        for entity_name in entitys:
            replace_text = entity_dict[entity_name]
            
            if content_type == 'TEXT':
                content_data['chatText'] = re.sub('{{'+f'{entity_name}'+'}}',replace_text, content_data['chatText'])
                
            elif content_type == 'CARD':
                content_data['cardItem']['title'] = re.sub('{{'+f'{entity_name}'+'}}',replace_text, content_data['cardItem']['title'])
                content_data['cardItem']['description'] = re.sub('{{'+f'{entity_name}'+'}}',replace_text, content_data['cardItem']['description'])
                
            elif content_type == 'LIST':
                content_data['listTitle'] = re.sub('{{'+f'{entity_name}'+'}}',replace_text, content_data['listTitle'])
                for list_item in content_data['listItem']:
                    list_item['subject'] = re.sub('{{'+f'{entity_name}'+'}}',replace_text, list_item['subject'])
                    list_item['desc'] = re.sub('{{'+f'{entity_name}'+'}}',replace_text, list_item['desc'])
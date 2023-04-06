'''
모듈설명 : text 전처리 함수
작성자 : 허윤성
버전 : 1.0.0
생성일자 : 2022.07.26
최종수정일자 : 2022.07.26
최종수정자 : 허윤성
최종수정내용 : 최초생성
참조 파일 구성 : 
참조파일 위치 : 
'''

from konlpy.tag import Kkma
from hanspell import spell_checker

kkm = Kkma()
def text_preprocessing(text):
    '''
    맞춤법 수정 -> 조사 제거 -> 맞춤법 수정
    
    Parameters
    ----------
    text : str
        입력 텍스트, 한글
    
    Returns
    ----------
    text : str
        전처리 후 text
    '''
    text = spell_checker.check(text).checked
    # text = ' '.join([word for word, pos in kkm.pos(text) if pos[0] not in ['J']])
    text = spell_checker.check(text).checked
    text = text.replace('이상 지질', '이상지질')
    return text
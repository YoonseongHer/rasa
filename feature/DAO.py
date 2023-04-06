from pymssql import connect
from configparser import ConfigParser

config = ConfigParser()
config.read('config//db_config.ini', encoding='utf-8') 

server = config['DB']['server']
database = config['DB']['database']
username = config['DB']['username']
password = config['DB']['password']

class DAO:
    '''
    master DB와 연결하여 작업을 처리
    '''
    def connect(self):
        '''
        DB connection을 수행
        
        Parameters
        ----------
        server : str
            DB 서버 주소
        
        username : str
            사용자 ID
        
        password : str
            사용자 비밀번호
        
        database : str
            DB 이름
            
        Returns
        ----------
        db connection
        '''
        return connect(server , username, password, database)
    
    def select(self, target, start_datetime, end_datetime=30000000):
        '''
        연결된 DB [AIM_BI.dbo.v_all_exam_all_period] 테이블에서 select 문을 수행하여 데이터를 가져온다.
        
        Parameters
        ----------
        target : list or tuple
            where절에 사용되는 group2 인자
        
        datetime : int (YYYYMMDD)
            where절에 사용되는 exam_date 인자
            
        Returns
        ----------
        list of tuple
            각 row는 하나의 tuple로 전체는 list로 되어있다. 
        '''
        cnxn = self.connect()
        cursor = cnxn.cursor()
        
        target = str(target).replace('[','(').replace(']',')')
        cursor.execute(f'''SELECT mem_id, comp_code, goods_code, exam_date, group1, group2, exam_data, general_op, grade_op
                            from AIM_BI.dbo.v_all_exam_all_period vaeap
                            where exam_date between {start_datetime} and {end_datetime}
                            and group2 in {target} 
                            order by 4,1,2,3''')
        row = cursor.fetchall()
        cnxn.close()
        return row
    
    def insert(self,df):
        '''
        연결된 DB [AIM_BI.dbo.v_all_exam_all_period] 테이블에서 insert 문을 수행하여 데이터를 입력한다.
        
        Parameters
        ----------
        df : pandas.DateFrame
            mem_id, comp_code, goods_code, exam_date, exam_text, exam_overall_text, exam_result, prd_rlt, txt_tagging 가 순서대로 포함된 dataframe
        '''
        cnxn = self.connect()
        cursor = cnxn.cursor()
        for mem_id,comp_code,goods_code,exam_date,group1,group2,exam_text,exam_overall_text,exam_result,prd_rlt,txt_tagging in df.values:
    
            row = cursor.execute(f'''INSERT INTO AIM_BI.DBO.ETFT_EXAM_PRD_RLT_TEMP001 
                            (MEM_ID, COMP_CODE, GOODS_CODE, EXAM_DATE, GROUP1, GROUP2, EXAM_DATA,GENERAL_OP,GRADE_OP,PRD_RLT,TXT_TAGGING,INST_YMD) 
                            VALUES ('{mem_id}','{comp_code}','{goods_code}','{exam_date}','{group1}','{group2}'
                            ,'{exam_text}','{exam_overall_text}','{exam_result}','{prd_rlt}','{txt_tagging}', GETDATE()) ; ''')

        cnxn.commit()
        cnxn.close()
    
    def update(self,df):
        '''
        연결된 DB [AIM_BI.dbo.v_all_exam_all_period] 테이블에서 update 문을 수행하여 데이터를 입력한다.
        
        Parameters
        ----------
        df : pandas.DateFrame
            mem_id, comp_code, goods_code, exam_date, exam_text, exam_overall_text, exam_result, prd_rlt, txt_tagging 가 순서대로 포함된 dataframe
        '''
        cnxn = self.connect()
        cursor = cnxn.cursor()
        for mem_id,comp_code,goods_code,exam_date,group1,group2,exam_text,exam_overall_text,exam_result,prd_rlt,txt_tagging in df.values:
    
            row = cursor.execute(f'''UPDATE AIM_BI.DBO.ETFT_EXAM_PRD_RLT_TEMP001 set PRD_RLT = '{prd_rlt}',TXT_TAGGING = '{txt_tagging}' ,INST_YMD = GETDATE() WHERE MEM_ID = '{mem_id}' and  COMP_CODE = '{comp_code}' and  GOODS_CODE = '{goods_code}' and  EXAM_DATE = '{exam_date}' and  GROUP2 = '{group2}' ; ''')

        cnxn.commit()
        cnxn.close()
        
    def summary_keyword(self, target):
        '''
        키워드 Table 에서 검사별 키워드와 그 외 나머지 키워드를 반환한다. 요약 태깅을 위해 사용된다.
        
        Parameters
        ----------
        target : list or tuple
            검사이름이 들어있는 list, tuple
        
        Returns
        ----------
        key : set
            target에 포함된 검사의 키워드
        
        key_other : set
            target에 포함된 검사의 키워드를 제외한 나머지 키워드
            
        '''
        cnxn = self.connect()
        cursor = cnxn.cursor()
        row = cursor.execute(''' SELECT summary_kywrd from AIM_BI.dbo.EXAM_SUMMARY_KEYRWORDS_INFO_TEMP001; ''')
        row = cursor.fetchall()
        key_all = set(sum(row,()))
        
        target = str(target).replace('[','(').replace(']',')')
        row = cursor.execute(f'''SELECT summary_kywrd from AIM_BI.dbo.EXAM_SUMMARY_KEYRWORDS_INFO_TEMP001 where group2 in {target};''')
        row = cursor.fetchall()
        key = set(sum(row,()))
        cnxn.close()
        
        key_other = key_all-(key-key_all)
        
        return key, key_other
    
    def severe_keyword(self, target):
        '''
        키워드 Table 에서 검사별 중증 유소견 키워드를 반환한다.
        
        Parameters
        ----------
        target : list or tuple
            검사이름이 들어있는 list, tuple
        
        Returns
        ----------
        key : list
            target에 포함된 검사의 중증 유소견 키워드
            
        '''
        cnxn = self.connect()
        cursor = cnxn.cursor() 
        target = str(target).replace('[','(').replace(']',')')
        row = cursor.execute(f'''SELECT severe_kywrd from AIM_BI.dbo.EXAM_SEVERE_KEYRWORDS_INFO_TEMP001 where group2 in {target};''')
        row = cursor.fetchall()
        key = set(sum(row,()))
        cnxn.close()

        return list(key)
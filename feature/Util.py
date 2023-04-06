'''
모듈설명 : util function
작성자 : 허윤성
버전 : 1.0.0
생성일자 : 2023.04.04
최종수정일자 : 2023.04.04
최종수정자 : 허윤성
최종수정내용 : 최초생성
참조 파일 구성 : 
참조파일 위치 : 
'''


def force_sync(fn):
    import functools
    '''
    turn an async function to sync function
    '''
    import asyncio

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        if asyncio.iscoroutine(res):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(res)
        return res

    return wrapper
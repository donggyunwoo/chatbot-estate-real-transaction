from pprint import pprint
import requests, json
import pandas as pd
from bs4 import BeautifulSoup as bs
import lxml
import aiohttp, asyncio
import yaml

with open('./config.yaml', 'r') as f:
    conf = yaml.safe_load(f)

key = conf['key']
doro_api = conf['doroapi']

def get_addr_code(response: list):
    ## 주소 정확도 or 다른 요구사항이 생기면 방식 추가 하기로.
    print(response)
    response = response[0]
    addr_gu_code = response.get('admCd')
    addr_pnu_code = response.get('bdMgtSn')
    print(addr_gu_code, addr_pnu_code)
    return addr_gu_code[:5], addr_pnu_code[:19]

async def request_doro_api(addr: str):
    doro_api_url = f'https://www.juso.go.kr/addrlink/addrLinkApi.do?currentPage=1&countPerPage=50&confmKey={doro_api}&firstSort=location&resultType=json&keyword='

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=doro_api_url+addr, ssl=False, timeout=5) as response:
                res = await response.json()        
        if res.get('results').get('common').get('errorCode') != '0':
            raise Exception(f"도로면 주소api error : {res.get('results').get('common').get('errorMessage')}")
        elif not res.get('results').get('juso'):
            raise Exception(f"{addr} 도로명 주소 결과 없음")
        addr_gu_code, addr_pnu_code = get_addr_code(res.get('results').get('juso'))
    except Exception as e:
        print(e)
        return 'error'
    
    return addr_gu_code

def get_building_info(response: list):
    response = response[0]
    '''
    mainPrposCodeNm
    detailPrposCodeNm
    '''



async def request_building_info(pnu:str):
    url = 'http://apis.data.go.kr/1611000/nsdi/BuildingUseService/attr/getBuildingUse'
    params ={'serviceKey' : f'{key}', 'pageNo' : '1', 'numOfRows' : '40', 'pnu' : f'{pnu}', 'format' : 'json' }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=params) as response:
                res = await response.json()
        res = res.get('buildingUses')
        if not res or res.get('totalCount')=='0' or res.get('totalCount') is None:
            raise Exception(f'건물정보 없거나 에러')
        get_building_info(res.get('field'))
        
    except Exception as e:
        print('def request_building_info')
        print(e)
        
    return

async def main_test(test_case: list):
    list_code = await asyncio.gather(*[request_doro_api(addr) for addr in testcase])
    
    return list_code




if __name__ == '__main__':
    # testcase = ['서울 중구 동호로24길 27-13', '장충동2가 211', '서울시 강동구 암사동 513-29','충북 청주시 흥덕구 대농로 55']
    testcase = ['서울시 강남구 역삼동 152', '서울 강남 역삼동 737']
    r = asyncio.run(main_test(test_case=testcase))

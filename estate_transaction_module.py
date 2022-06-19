from pprint import pprint
import requests, json
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
    response = response[0]
    addr_gu_code = response.get('admCd')
    addr_pnu_code = response.get('bdMgtSn')
    return addr_gu_code[:5], addr_pnu_code[:19]

async def request_doro_api(addr: str):
    doro_api_url = f'https://www.juso.go.kr/addrlink/addrLinkApi.do?currentPage=1&countPerPage=50&confmKey={doro_api}&firstSort=location&resultType=json&keyword='
    addr_gu_code, addr_pnu_code = '', '' 
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
    
    return addr_gu_code, addr_pnu_code

def get_building_info(response: list):
    response = response[0]
    pprint(response)
    '''
    mainPrposCodeNm
    detailPrposCodeNm
    '''
    return 


async def request_building_info(pnu:str):
    url = 'http://apis.data.go.kr/1611000/nsdi/BuildingUseService/attr/getBuildingUse'
    params = {'serviceKey' : f'{key}', 'pageNo' : '1', 'numOfRows' : '40', 'pnu' : f'{pnu}', 'format' : 'json' }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, params=params) as response:
                res = await response.json()
        res = res.get('buildingUses')
        if not res or res.get('totalCount')=='0' or res.get('totalCount') is None:
            raise Exception(f'error : {pnu} : 건물정보 없거나 에러')
        info = get_building_info(res.get('field'))
        
    except Exception as e:
        print('def request_building_info')
        print(e)
        
    return

async def main_test(test_case: list):
    list_code = await asyncio.gather(*[request_doro_api(addr) for addr in testcase])
    for addr_code in list_code:
        if not addr_code[0]: continue
    await asyncio.gather(*[request_building_info(pnu[1]) for pnu in list_code])


        
    return list_code




if __name__ == '__main__':
    # testcase = ['서울 중구 동호로24길 27-13', '장충동2가 211', '서울시 강동구 암사동 513-29','충북 청주시 흥덕구 대농로 55']
    testcase = ['서울 강남 역삼동 737', '장충동2가 211','서울시 송파구 송파대로 345','충북 청주시 흥덕구 대농로 55', '충북 청주시 흥덕구 복대동 2397']
    r = asyncio.run(main_test(test_case=testcase))
'''
def request_building_info
error : 1114014400101860044 : 건물정보 없거나 에러
def request_building_info
error : 1171010700104790000 : 건물정보 없거나 에러
def request_building_info
error : 4311311400102880014 : 건물정보 없거나 에러
{'agbldgSeCode': '1',
 'agbldgSeCodeNm': '일반건축물',
 'btlRt': '42.57',
 'buldBildngAr': '5600.51',
 'buldDongNm': None,
 'buldHg': '202.65',
 'buldIdntfcNo': '12777',
 'buldKndCode': '2',
 'buldKndCodeNm': '일반건축물대방',
 'buldMainAtachSeCode': '0',
 'buldMainAtachSeCodeNm': '주건축물',
 'buldNm': '강남파이낸스센터',
 'buldPlotAr': '13156.7',
 'buldPrposClCode': '2',
 'buldPrposClCodeNm': '상업용',
 'buldTotar': '212615.29',
 'detailPrposCode': '14299',
 'detailPrposCodeNm': '기타일반업무시설',
 'gisIdntfcNo': '2001203158584442021200000000',
 'groundFloorCo': '45',
 'lastUpdtDt': '2022-02-23',
 'ldCode': '1168010100',
 'ldCodeNm': '서울특별시 강남구 역삼동',
 'mainPrposCode': '14000',
 'mainPrposCodeNm': '업무시설',
 'measrmtRt': '995.19',
 'mnnmSlno': '737',
 'pnu': '1168010100107370000',
 'prmisnDe': '1995-05-04',
 'regstrSeCode': '1',
 'regstrSeCodeNm': '일반',
 'strctCode': '42',
 'strctCodeNm': '철골철근콘크리트구조',
 'undgrndFloorCo': '8',
 'useConfmDe': '2001-07-31'}
{'agbldgSeCode': '1',
 'agbldgSeCodeNm': '일반건축물',
 'btlRt': '0',
 'buldBildngAr': '122.32',
 'buldDongNm': None,
 'buldHg': '0',
 'buldIdntfcNo': '126117',
 'buldKndCode': '2',
 'buldKndCodeNm': '일반건축물대방',
 'buldMainAtachSeCode': '0',
 'buldMainAtachSeCodeNm': '주건축물',
 'buldNm': None,
 'buldPlotAr': '0',
 'buldPrposClCode': '1',
 'buldPrposClCodeNm': '주거용',
 'buldTotar': '489.28',
 'detailPrposCode': '01003',
 'detailPrposCodeNm': '다가구주택',
 'gisIdntfcNo': '1991240067273471562200000000',
 'groundFloorCo': '3',
 'lastUpdtDt': '2022-02-23',
 'ldCode': '4311311400',
 'ldCodeNm': '충청북도 청주시 흥덕구 복대동',
 'mainPrposCode': '01000',
 'mainPrposCodeNm': '단독주택',
 'measrmtRt': '0',
 'mnnmSlno': '2397',
 'pnu': '4311311400123970000',
 'prmisnDe': '1991-12-09',
 'regstrSeCode': '1',
 'regstrSeCodeNm': '일반',
 'strctCode': '21',
 'strctCodeNm': '철근콘크리트구조',
 'undgrndFloorCo': '1',
 'useConfmDe': '1991-07-22'}
'''
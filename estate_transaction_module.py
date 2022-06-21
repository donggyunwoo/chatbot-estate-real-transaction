from cmath import inf
from pprint import pprint
import aiohttp, asyncio
from bs4 import BeautifulSoup as bs
import yaml
from datetime import date
from dateutil.relativedelta import relativedelta

with open('./config.yaml', 'r') as f:
    conf = yaml.safe_load(f)

key = conf['key']
doro_api = conf['doroapi']
dict_estate_url = {
    '아파트':[
        ('http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?','아파트 매매 자료'),
        ('http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?','아파트 전월세 자료'),
        ('http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSilvTrade','아파트 분양권 자료')
    ],
    '단독/다가구':[
        ('http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHTrade','단독/다가구 매매 자료'),
        ('http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHRent','단독/다가구 전월세 자료')
    ],
    '다세대/연립':[
        ('http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcRHTrade','다세대/연립 매매 자료'),
        ('http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcRHRent','다세대/연립 전월세 자료')
    ],
    '오피스텔':[
        ('http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcOffiTrade','오피스텔 매매 자료'),
        ('http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcOffiRent','오피스텔 전월세 자료')
    ],
    '상업/업무용':[
        ('http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcNrgTrade','상업/업무용 매매 자료')
    ],
    '토지':[
        ('http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcLandTrade','토지 매매 자료')
    ],
}

def get_addr_code(response: list):
    ## 주소 정확도 or 다른 요구사항이 생기면 방식 추가 하기로.
    response = response[0]
    pprint(response)
    addr_gu_code = response.get('admCd')
    return addr_gu_code[:5]


async def request_doro_api(addr: str):
    doro_api_url = f'https://www.juso.go.kr/addrlink/addrLinkApi.do?currentPage=1&countPerPage=50&confmKey={doro_api}&firstSort=location&resultType=json&keyword='
    addr_gu_code = ''
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=doro_api_url+addr, ssl=False, timeout=10) as response:
                res = await response.json()        
        if res.get('results').get('common').get('errorCode') != '0':
            raise Exception(f"도로면 주소api error : {res.get('results').get('common').get('errorMessage')}")
        elif not res.get('results').get('juso'):
            raise Exception(f"{addr} 도로명 주소 결과 없음")
        addr_gu_code = get_addr_code(res.get('results').get('juso'))
    except Exception as e:
        print(e)
    
    return addr_gu_code

def pre_processing_date(start:str, end:str)->list:
    ## 값이 어떻게 들어오냐에 따라서 수정.
    list_date = []
    if not isinstance(start, str) or not isinstance(end, str):
        start, end = str(start), str(end)
    y_start, m_start = map(int, start.split('/'))
    y_end, m_end = map(int, end.split('/'))
    date_start = date(year=y_start, month=m_start, day=1 )
    date_end = date(year=y_end, month=m_end, day=1)
    if date_start>date_end:
        date_start, date_end = date_end, date_start
    while 1:
        list_date.append(date_start.strftime('%Y%m'))
        date_start = date_start + relativedelta(months=1)
        if date_start == date_end:
            list_date.append(date_start.strftime('%Y%m'))
            break
    print(list_date)
    return list_date

def pre_processing_building_type(context: str) -> list:
    list_url = []
    if '아파트' in context:
        list_url.extend(dict_estate_url.get('아파트'))
    if '단독' in context or '다가구' in context:
        list_url.extend(dict_estate_url.get('단독/다가구'))
    if '다세대' in context or '연립' in context:
        list_url.extend(dict_estate_url.get('다세대/연립'))
    if '오피스텔' in context:
        list_url.extend(dict_estate_url.get('오피스텔'))
    if '상업' in context or '업무용' in context:
        list_url.extend(dict_estate_url.get('상업/업무용'))
    if '토지' in context:
        list_url.extend(dict_estate_url.get('토지'))
    return list_url

async def request_estate_api(url:str, type_api:str, date:str, code:str):
    params ={'serviceKey' : key, 'LAWD_CD' : code, 'DEAL_YMD' : date }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, timeout=10, params=params) as response:
                res = await response.text()
        pprint(res)
    except Exception as e:
        print('request_estate_api', e)
    return

async def async_real_estate_transaction(estate_info: list):
    '''
    input : estate_info = [start_date, end_date, [거래 유형], 법정동주소]
    output : [start_date, end_date, [거래 유형], 법정동주소, 동 코드]
    '''
    list_type_url = []
    list_date = []
    list_code = await asyncio.gather(*[request_doro_api(estate_info[-1])])
    estate_info.append(list_code[0])
    list_type_url = pre_processing_building_type(estate_info[2])
    list_date = pre_processing_date(estate_info[0], estate_info[1])
    list_req_info = []
    for url in list_type_url:
        for date in list_date:
            list_req_info.append([url[0], url[1], date, estate_info[-1]])
    await asyncio.gather(*[request_estate_api(url=info[0], type_api=info[1], date=info[2], code=info[3]) for info in list_req_info])
    return list_req_info




if __name__ == '__main__':
    testcase = [
        # ['22/01', '22/04', '아파트, 단독, 다세대', '서울시 강남구 역삼동'],
        ['2022/01', '2022/02', '아파트', '서울 강남 역삼'],
        # ['22/01', '22/04', '아파트, 단독, 다세대', '서울시 강동구 암사동'],
        # ['2022/01', '2022/04', '다세대', '충북 청주시 서원구 남이면 가좌리'],
        # ['2021/01', '2022/04', '아파트', '서울 중구 장충동 1가'],
    ]
    for item in testcase:
        # break
        r = asyncio.run(async_real_estate_transaction(estate_info=item))
        pprint(r)
    
    # pre_processing_date('2021/12', '2022/02')
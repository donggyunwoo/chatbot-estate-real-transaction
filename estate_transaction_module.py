from pprint import pprint
import aiohttp, asyncio
import yaml
from datetime import date

with open('./config.yaml', 'r') as f:
    conf = yaml.safe_load(f)

key = conf['key']
doro_api = conf['doroapi']
dict_estate_url = {
    '아파트':[
        'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?',
        'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptRent?',
        'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSilvTrade'
    ],
    '단독/다가구':[
        'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHTrade',
        'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcSHRent'  
    ],
    '다세대/연립':[
        'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcRHTrade',
        'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcRHRent'
    ],
    '오피스텔':[
        'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcOffiTrade',
        'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcOffiRent'
    ],
    '상업/업무용':[
        'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcNrgTrade',
    ],
    '토지':[
        'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcLandTrade',
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
            async with session.get(url=doro_api_url+addr, ssl=False, timeout=5) as response:
                res = await response.json()        
        if res.get('results').get('common').get('errorCode') != '0':
            raise Exception(f"도로면 주소api error : {res.get('results').get('common').get('errorMessage')}")
        elif not res.get('results').get('juso'):
            raise Exception(f"{addr} 도로명 주소 결과 없음")
        addr_gu_code = get_addr_code(res.get('results').get('juso'))
    except Exception as e:
        print(e)
    
    return addr_gu_code

def pre_processing_date(start, end):
    return

async def main_test(estate_info: list):
    '''
    input : estate_info = [start_date, end_date, [거래 유형], 법정동주소]
    output : [start_date, end_date, [거래 유형], 법정동주소, 동 코드]
    '''
    list_code = await asyncio.gather(*[request_doro_api(addr[-1]) for addr in estate_info])
    n = len(estate_info)
    for idx in range(n):
        estate_info[idx].append(list_code[idx])
    

        
    return estate_info




if __name__ == '__main__':
    testcase = [
        ['22/01', '22/04', '아파트, 단독, 다세대', '서울시 강남구 역삼동'],
        ['22/01', '22/04', '아파트, 단독, 다세대', '서울시 강동구 암사동'],
        ['22/01', '22/04', '아파트, 단독, 다세대', '충북 청주시 흥덕구 복대동'],
    ]
    r = asyncio.run(main_test(estate_info=testcase))
    pprint(r)
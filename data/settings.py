from random import choice

import httpx
from httpx import Headers


def headers() -> Headers:
    return {
        'accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'uz,en-US;q=0.9,en;q=0.8,ru;q=0.7',
        'cookie': choice(cookies),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }


cookies = [
    'ds_user_id=49596389611; sessionid=49596389611%3ATpZmJi21u7X7nx%3A29%3AAYeH5AovheMlulzKBN_S2YIXA5OCniOQuZoKIgJjKA',
    # 'ds_user_id=49596389611; sessionid=49596389611%3AtSyEduyT78X2j4%3A29%3AAYc9YQwb9yzlp0Nua7dPbto2Ls1PBAEJ68R2WiNzpw',
    # 'ds_user_id=49596389611; sessionid=49596389611%3AtSyEduyT78X2j4%3A29%3AAYcMbuZWxrA195ALNQIM2LZ6z_4u7h6wI-yx68kaRQ',
]


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
    'ds_user_id=49596389611; sessionid=49596389611%3AtSyEduyT78X2j4%3A29%3AAYc9YQwb9yzlp0Nua7dPbto2Ls1PBAEJ68R2WiNzpw',
    'ds_user_id=49596389611; sessionid=49596389611%3AtSyEduyT78X2j4%3A29%3AAYcMbuZWxrA195ALNQIM2LZ6z_4u7h6wI-yx68kaRQ',
]

# headers2 = {
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#     'accept-encoding': 'gzip, deflate, br',
#     'accept-language': 'uz,en-US;q=0.9,en;q=0.8,ru;q=0.7',
#     'cookie': 'ig_did=F63C5130-AB61-473B-BC1A-CB21E759AD09; datr=3pBCZYAzHTAo_AMkO34LHYD2; ig_nrcb=1; mid=ZUKQ7QALAAGT6m7V-GOfLJsRGPHn; ds_user_id=49596389611; shbid="7015\05449596389611\0541732914387:01f76686e1238f7edc44baf9426f221c97495e875e4031ab4392036839f5fe83a03025bb"; shbts="1701378387\05449596389611\0541732914387:01f7e1bf51cce624bfa24aeb5792529e4d929d404872f7e864f551946c5858df42460f78"; dpr=1.125; csrftoken=c4kJdIkBeAg8dZdMPWZSCTxU0ejLEgQk; sessionid=49596389611%3AtSyEduyT78X2j4%3A29%3AAYc9YQwb9yzlp0Nua7dPbto2Ls1PBAEJ68R2WiNzpw; rur="LDC\05449596389611\0541733095720:01f78c6e3e47b9f4efbe3c5cca76198e246fe216b944a49e324a00e4e85af5a9fc9fd8ee"',
#     'dpr': '1.125',
#     'sec-ch-prefers-color-scheme': 'dark',
#     'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
#     'sec-ch-ua-full-version-list': '"Google Chrome";v="119.0.6045.200", "Chromium";v="119.0.6045.200", "Not?A_Brand";v="24.0.0.0"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-model': '""',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-ch-ua-platform-version': '"15.0.0"',
#     'sec-fetch-dest': 'document',
#     'sec-fetch-mode': 'navigate',
#     'sec-fetch-site': 'none',
#     'sec-fetch-user': '?1',
#     'upgrade-insecure-requests': '1',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
#     'viewport-width': '1707'
# }

import json
import requests


_pv0 = None


def getPubKey():
    global _pv0

    url = "https://cas.hnu.edu.cn/cas/v2/getPubKey"

    payload = {}
    from login.loginHNU import JSESSIONID
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Host': 'cas.hnu.edu.cn',
        'Referer': 'https://cas.hnu.edu.cn/cas/login?v=0.39953932396441916',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Cookie': f'JSESSIONID={JSESSIONID}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)
    exponent = data["exponent"]
    modulus = data["modulus"]

    # store necessary data
    _pv0 = response.cookies["_pv0"]

    return exponent, modulus

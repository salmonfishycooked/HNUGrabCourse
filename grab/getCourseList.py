import json
import requests

from grab.decrypt2 import decrypt2
from login.loginHNU import loginEA


# getCourseList will grab all courses of hnu
def getCourseList():
    print("> HOLO: I'm getting the course list...")

    try:
        sessionId, SINDEXCOOKIE = loginEA()
        url = "http://yjsxt.hnu.edu.cn/gmis/" + sessionId + "/student/pygl/xswsxk_kb_list"
        payload = {}
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'yjsxt.hnu.edu.cn',
            'Origin': 'http://yjsxt.hnu.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Cookie': f'__SINDEXCOOKIE__={SINDEXCOOKIE}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        realData = decrypt2(response.text)
        total = json.loads(realData)["total"]

        courses = []
        for lb in range(1, 4):
            payload1 = f"page=1&rows={total}&lb={lb}"
            response = requests.request("POST", url, headers=headers, data=payload1)
            realDataJson = decrypt2(response.text)
            realData = json.loads(realDataJson)
            courses += realData["kc"]

        with open("courses.json", "w") as f:
            f.write(json.dumps(courses, ensure_ascii=False))
    except Exception as e:
        print("> HOLO: Maybe we shouldn't use VPN to access.")
        exit(1)

import getpass
import json
import os
import re
import subprocess
import requests

from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

from login.getPubKey import getPubKey


# necessary cookie
JSESSIONID_CAS = None
JSESSIONID = None
_pf0 = None
_pc0 = None
_pv0 = None
iPlanetDirectoryPro = None
ysydOtp = None
_syz = None

action, executionValue = None, None


def encryptRSA(text, publicExponent, modulus):
    try:
        process = subprocess.run(
            ["node", os.path.join(os.getcwd(), "login", "encryptRSA.js"), text, publicExponent, modulus],
            capture_output=True,
            text=True
        )
    except Exception as e:
        print("> HOLO: Make sure you have installed node.js.")
        exit(1)

    return process.stdout


def _accessMainPage():
    global JSESSIONID_CAS, action, executionValue

    url = "https://cas.hnu.edu.cn/cas/login"
    payload = {}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Host': 'cas.hnu.edu.cn',
        'Connection': 'keep-alive'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    JSESSIONID_CAS = response.cookies["JSESSIONID"]

    # get execution field
    soup = BeautifulSoup(response.text, "html.parser")
    executionInput = soup.find("input", {"name": "execution"})
    if executionInput and executionInput.has_attr("value"):
        executionValue = executionInput["value"]

    # get action uri
    action = None
    soup = BeautifulSoup(response.text, "html.parser")
    executionInput = soup.find("form", {"id": "fm1"})
    if executionInput and executionInput.has_attr("action"):
        action = executionInput["action"].strip()


def _getAnotherSessionId():
    global JSESSIONID

    url = "https://cas.hnu.edu.cn/favicon.ico"
    payload = {}
    headers = {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Host': 'cas.hnu.edu.cn',
        'Referer': 'https://cas.hnu.edu.cn/cas/login',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Connection': 'keep-alive',
    }

    response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
    JSESSIONID = response.cookies["JSESSIONID"]


def _doLogin(username, encryptedPwd):
    global _pv0, _pf0, _pc0, _syz, iPlanetDirectoryPro, ysydOtp

    url = "https://cas.hnu.edu.cn/cas/" + action
    payload = f"username={username}&password={encryptedPwd}&execution={executionValue}&authcode=&_eventId=submit"
    from login.getPubKey import _pv0
    _pv0 = _pv0
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Host': 'cas.hnu.edu.cn',
        'Origin': 'https://cas.hnu.edu.cn',
        'Referer': 'https://cas.hnu.edu.cn/cas/login',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Upgrade-Insecure-Request': '1',
        'Cookie': f'JSESSIONID={JSESSIONID_CAS};JSESSIONID={JSESSIONID};_pv0={_pv0}',
        'Connection': 'keep-alive'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
        if response.status_code == 403:
            print("> HOLO: Your account has been blocked, try 10 minutes later!")
            exit(1)
        if "_pc0" not in response.cookies:
            print("> HOLO: Incorrect username or password! How many times should I tell you?")
            exit(1)

        _pf0 = response.cookies["_pf0"]
        ysydOtp = response.cookies["ysydOtp"]
        _pc0 = response.cookies["_pc0"]
        iPlanetDirectoryPro = response.cookies["iPlanetDirectoryPro"]
        _syz = response.cookies["_syz"]
    except Exception as e:
        print("> HOLO: Frequent login. Try again later! Now it's coffee time!")
        exit(1)


def _makeNecessaryCookie():
    return (f"JSESSIONID={JSESSIONID_CAS};JSESSIONID={JSESSIONID};_pv0={_pv0};_pc0={_pc0};_pf0={_pf0};"
            f"ysydOtp={ysydOtp};iPlanetDirectoryPro={iPlanetDirectoryPro};_syz={_syz}")


def _getPersonalInfo():
    # ----- phase 1 -----
    url = "https://pt.hnu.edu.cn/personal-center"
    payload = {}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Host': 'pt.hnu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Connection': 'keep-alive'
    }
    response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

    route = response.cookies["route"]

    # ----- phase 2 -----
    url = response.headers["Location"]
    payload = {}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Host': 'cas.hnu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Connection': 'keep-alive',
        "Cookie": _makeNecessaryCookie()
    }
    response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

    # ----- phase 3 -----
    url = response.headers["Location"]
    payload = {}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Host': 'pt.hnu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Connection': 'keep-alive',
        "Cookie": f"route={route}"
    }
    response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
    wisportalId = response.cookies["wisportalId"]

    # ----- phase 4 -----
    url = "https://pt.hnu.edu.cn/api/basic/info"
    payload = {}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Host': 'pt.hnu.edu.cn',
        'Referer': 'https://pt.hnu.edu.cn/personal-center',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Connection': 'keep-alive',
        "Cookie": f"route={route};wisportalId={wisportalId}"
    }
    response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

    personalInfo = json.loads(response.text)["data"]
    name, sid = personalInfo["nc"], personalInfo["yhm"]
    print(f"> HOLO: {sid} {name}, Welcome Back! Now is {datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z %z")}")


# login for http://cas.hnu.edu.cn/cas/login
def loginHNU():
    print("> HOLO: Now Login to http://cas.hnu.edu.cn/cas/login")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    _accessMainPage()
    _getAnotherSessionId()

    exponent, modulus = getPubKey()

    encryptedPwd = encryptRSA(password[::-1], exponent, modulus)
    _doLogin(username, encryptedPwd)
    _getPersonalInfo()


# login for http://yjsxt.hnu.edu.cn/gmis
def loginEA():
    try:
        # ----- phase 1 -----
        url = "http://cas.hnu.edu.cn/cas/login?service=http://yjsxt.hnu.edu.cn/gmis/oauthLogin/hndxnew"
        payload = {}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Host': 'cas.hnu.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Connection': 'keep-alive',
            "Cookie": _makeNecessaryCookie()
        }
        response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

        # ----- phase 2 -----
        url = response.headers["Location"]
        payload = {}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Host': 'yjsxt.hnu.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Connection': 'keep-alive'
        }
        response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

        # ----- phase 3 -----
        url = "http://yjsxt.hnu.edu.cn" + response.headers["Location"]
        payload = {}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Host': 'yjsxt.hnu.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Connection': 'keep-alive'
        }
        response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)

        SINDEXCOOKIE = response.cookies["__SINDEXCOOKIE__"]
        sessionId = re.match(r"/gmis/(\(S\(\w+\)\))/student/default/index", response.headers["Location"]).group(1)

        return sessionId, SINDEXCOOKIE
    except Exception as e:
        print("> HOLO: I've caught an exception in LoginEA.", e)
        return None, None

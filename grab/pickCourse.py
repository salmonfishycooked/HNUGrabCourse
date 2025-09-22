import itertools
import threading
import time
import requests

from rich.live import Live
from rich.table import Table

from config import config
from grab.decrypt2 import decrypt2
from login.loginHNU import loginEA


msgCourseFull = "AdTcqNcOwvDoROlqROpvh/f0h+edDiNfk9m94J1XhDJhishB/hnuPH+Pb9wVa5e2"
msgCourseGrabbed = "PsIWXMwEVHKbW7y9q4bgVg=="
msgCoursePicked = "AdTcqNcOwvDoROlqROpvh7KcHx2VZXAc7y0F5vzAm+7f44L0qWpsjr0Ff3iwAvSkHIIVJsQkCgdRBPig76vZVupfmjlKps41cq+irsrGzAblV0itXJuwHXWWyimkXpVV"


url = None
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Host': 'yjsxt.hnu.edu.cn',
    'Origin': 'http://yjsxt.hnu.edu.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Cookie': ''
}


nRunningTasks = 0
_tasks = []
_status = {}
_spinner = ["|", "/", "-", "\\"]


runningState = "GRABBING"
finishState = "✔ WE GOT IT"
exceptionState = "⚠ EXCEPTION"
pickedState = ":) BUT WE'VE GOT THIS ALREADY"


stopEvent = threading.Event()


def updateUrl():
    global url, headers

    while any(_status[task]["state"] == runningState for task in _tasks):
        stopEvent.wait(999)
        sessionId, SINDEXCOOKIE = loginEA()
        if sessionId is None: continue

        url = "http://yjsxt.hnu.edu.cn/gmis/"+ sessionId +"/student/pygl/xswsxk_kb_xk"
        headers["cookie"] = f"__SINDEXCOOKIE__={SINDEXCOOKIE}"


def drawProgressBar():
    def renderTable(frame):
        table = Table()
        table.add_column("Course ID")
        table.add_column("Course Name")
        table.add_column("Status")
        table.add_column("Tries")
        for task in _tasks:
            state = _status[task]["state"]
            tries = _status[task]["tries"]
            cname = _status[task]["cname"]
            displayState = f"{_spinner[frame % len(_spinner)]} {state}" if state == runningState else state
            table.add_row(task, cname, displayState, str(tries))
        return table

    with Live(renderTable(0), refresh_per_second=3) as live:
        frame = 0
        while any(_status[task]["state"] == runningState for task in _tasks):
            frame += 1
            live.update(renderTable(frame))
            time.sleep(0.33)
        frame += 1
        live.update(renderTable(frame))


def pickCourse(courseIds, courseNames):
    global url, headers, nRunningTasks

    sessionId, SINDEXCOOKIE = loginEA()
    url = "http://yjsxt.hnu.edu.cn/gmis/" + sessionId + "/student/pygl/xswsxk_kb_xk"
    headers["cookie"] = f"__SINDEXCOOKIE__={SINDEXCOOKIE}"

    print("> HOLO: I am trying my best to help you grab these courses. :)")

    for (cid, cname) in zip(courseIds, courseNames):
        nRunningTasks += 1
        _tasks.append(cid)
        _status[cid] = {"cname": cname, "state": runningState, "tries": 0}
        threading.Thread(target=_takeCourse, args=(cid, cname)).start()

    threading.Thread(target=drawProgressBar).start()
    threading.Thread(target=updateUrl).start()


def _takeCourse(courseId, courseName):
    global nRunningTasks

    payload = f'lb=1&bjid={courseId}'

    success = False
    for i in itertools.count():
        try:
            if not success:
                response = requests.request("POST", url, headers=headers, data=payload, timeout=5)
                _status[courseId]["tries"] += 1
                if response.text == msgCoursePicked:
                    _status[courseId]["state"] = pickedState
                    break
                if response.text != msgCourseGrabbed and response.text != msgCourseFull:
                    _status[courseId]["state"] = exceptionState
                    print(f"> HOLO have caught an grabbing accident of {courseName} ({courseId}): {decrypt2(response.text)}")
                    break

                success = True if response.text == msgCourseGrabbed else False
        except Exception as e:
            pass
            # print("holo caught an exception, but she will continue trying...")

        if success:
            _status[courseId]["state"] = finishState
            break

        time.sleep(config["timeInterval"])

    nRunningTasks -= 1
    if nRunningTasks == 0:
        stopEvent.set()

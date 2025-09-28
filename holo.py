# HNUGrabCourse
# Author: sharkie (https://github.com/salmonfishycooked)

import json

from config import config
from grab.getCourseList import getCourseList
from grab.pickCourse import pickCourse
from login.loginHNU import loginHNU


def readCourseMap():
    courseJson = []
    with open("courses.json", "r") as f:
        str = f.read()
        courseJson = json.loads(str)

    courseIdToName = {}
    for courseInfo in courseJson:
        courseIdToName[courseInfo["bjid"]] = courseInfo["bjmc"]

    return courseIdToName


def readCourseNeeded(filename):
    courseIds = []
    with open(filename, "r") as f:
        while True:
            s = f.readline()
            if len(s) == 0: break

            cid = s.strip()
            if len(cid) != 0:
                courseIds.append(cid)

    if len(courseIds) == 0:
        print(f"> HOLO: Why don't you wanna write any course id in your {config["courseFile"]}?")
        exit(1)

    courseIdToName = readCourseMap()
    courseNames = []
    for id in courseIds:
        if id not in courseIdToName:
            print(f"> HOLO: Are you serious? {id} is not in the course list.")
            exit(1)

        courseNames.append(courseIdToName[id])

    return courseIds, courseNames


def createPickFile():
    try:
        with open(config["courseFile"], "x", encoding="utf-8") as f:
            pass
    except FileExistsError:
        pass


if __name__ == "__main__":
    print("-------------------------------------------------------------------------------------------------")
    print("| This program is designed for someone who is a graduate of Hunan University to grab the course.")
    print("| Here is 🐺 HOLO 🐺, the Wise Wolf of Yoitsu.")
    print("| Author: sharkie (https://github.com/salmonfishycooked)")
    print("| Use HNU WIFI to get a faster experience.")
    print("| ⚠ BETTER NOT TO USE VPN! ⚠")
    print("-------------------------------------------------------------------------------------------------")

    loginHNU()

    getCourseList()
    createPickFile()

    input(f"> HOLO: Put course ids into {config["courseFile"]}, ready? (press enter)")
    courseIds, courseNames = [], []
    try:
        courseIds, courseNames = readCourseNeeded(config["courseFile"])
    except Exception as e:
        print(f"> HOLO: Have you just deleted the file {config["courseFile"]}?")
        exit(1)

    pickCourse(courseIds, courseNames)

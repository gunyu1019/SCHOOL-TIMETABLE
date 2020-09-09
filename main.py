import datetime
import requests
import os

import json

from PIL import Image
from io import BytesIO

directory = os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
if os.path.isfile(directory + "/key.txt"):
    key_file = open(directory + "/key.txt",mode='r')
    key = key_file.read()
    key_file.close()

if os.path.isfile(directory + "/config.txt"):
    config_file = open(directory + "/config.txt",mode='r',encoding='utf-8')
    config = config_file.readlines()
    config_file.close()
    config_json = {}
    for i in config:
        line = config.index(i)
        if i == "==== config.json ====\n":
            config_json = json.loads("".join(config[line+1:]))
    if config_json == {}:
        print("에러 발생(404): config 설정을 찾을 수 없습니다.")
    #key = config_json['key']
    school_name = config_json['school_nm']
    grade = config_json['grade']
    class_nm = config_json['class']
else:
    key = "NEIS-API 키를 작성하여 주세요!"
    school_name = "서울초등학교"
    grade = 1
    class_nm = 1

def name(name):
    tmp = name.replace("통합과학","통과").replace("통합사회","통사").replace("과학탐구실험","과탐").replace("활동","").replace("기술·가정","기가").replace("-","").replace("주제선택","주제").replace("(자)","").replace("(창)","")
    return tmp.replace("진로와 직업","진로").replace("즐거운생활","즐거운").replace("슬기로운생활","슬기로운").replace("바른생활","도덕").replace(" ","")

def main():
    header1 = {
        "Type":"json",
        "KEY":key,
        "SCHUL_NM":school_name
    }
    resp1 = requests.get("https://open.neis.go.kr/hub/schoolInfo",params=header1)
    json1 = json.loads(resp1.text)

    today = datetime.datetime.today()
    last_monday = today - datetime.timedelta(days = today.weekday())
    last_friday = today + datetime.timedelta(days = 4 - today.weekday())
    type_nm = json1['schoolInfo'][1]['row'][0]['SCHUL_KND_SC_NM']
    type_list = {"초등학교":"els","중학교":"mis","고등학교":"his","특수학교":"sps"}
    if not type_nm in type_list:
        print("에러 발생(404): 지원하지 않는 유형의 학교입니다. | 초등학교, 중학교, 고등학교만 지원합니다.")
        return

    header2 = {
        "Type":"json",
        "KEY":key,
        "ATPT_OFCDC_SC_CODE":json1['schoolInfo'][1]['row'][0]['ATPT_OFCDC_SC_CODE'],
        "SD_SCHUL_CODE":json1['schoolInfo'][1]['row'][0]['SD_SCHUL_CODE'],
        "GRADE":grade,
        "CLASS_NM":class_nm,
        "TI_FROM_YMD":last_monday.strftime('%Y%m%d'),
        "TI_TO_YMD":last_friday.strftime('%Y%m%d')
    }
    resp2 = requests.get(f"https://open.neis.go.kr/hub/{type_list[type_nm]}Timetable",params=header2)
    json2 = json.loads(resp2.text)
    if 'RESULT' in json2.keys():
        if 'CODE' in json2['RESULT'].keys():
            ercode = json2['RESULT']['CODE']
            if ercode == 'INFO-200':
                print("에러 발생(404): 학교를 찾지 못했습니다.")
                return

    class_name = [["" for col in range(7)] for row in range(5)]

    for i in json2[f'{type_list[type_nm]}Timetable'][1]['row']:
        i_class_name = i['ITRT_CNTNT']
        weekend = int(i['ALL_TI_YMD'])-int(last_monday.strftime('%Y%m%d'))
        class_name[weekend][int(i['PERIO'])-1] = name(i_class_name)

    weekend_list = ["월","화","수","목","금"]
    answer = "{"
    for i in class_name:
        weekend_name = weekend_list[class_name.index(i)]
        class_name_i = str(i).replace('\'','\"')
        answer += f",\"{weekend_name}\":{class_name_i}"
    answer = answer.replace(',','',1)
    answer += "}"
    header3 = {
        "text": answer
    }
    resp3 = requests.get("http://vz.kro.kr/sigan.php",params=header3)
    html = resp3.content
    filename = today.strftime('%Y-%m-%d %H-%M-%S')
    i = Image.open(BytesIO(html))
    i.save(f'{directory}/image/{filename}.png')
    return

if __name__ == "__main__":
    main()
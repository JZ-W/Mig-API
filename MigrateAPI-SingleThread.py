#coding = utf-8

# for single test case:
# Step 1: send post request
# Step 2: download dataurl and save to local

import requests
import json
import urllib.request
import traceback
import os
import time
import datetime

onlyHardDeco = False

url = "http://47.95.219.76:30008/api/rest/v1.0/tenants/ezhome/designs/migrate"

headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    }

def genPayloadJson(aliJobId,templateId,designId,onlyHardDeco,softAlgorithm):
    values = {
        "aliJobId" : aliJobId,
        "templateId" : templateId,
        "designId" : designId,
        "onlyHardDeco" : onlyHardDeco,
        "softAlgorithm" : "" 
    }
    print("payload: " + str(values))
    return values

def http_post(url,data_json):
    try:
        print("--------------sending post request -------------")
        jdata = json.dumps(data_json)
        response = requests.post(url, jdata, headers=headers)
        if response.status_code!= 200:
            print("--------------send post request failed -------------")
            return 0
        hjson = json.loads(response.content)
        if hjson["er"]!= -1:
            print("---------------API failed!-----------------")
            return 0
        else:
            datajsonUrl = hjson["data"][0]["dataUrl"]
            scenejsonUrl = hjson["data"][0]["sceneUrl"]
        # response.text is str
            return datajsonUrl, scenejsonUrl
    except:
        traceback.print_exc()


def bool_downloadUrl(url,fname,retrycount):
    i = 1
    while i<= retrycount:
        try:
            response = requests.get(url)
            print("trying", i, "/", retrycount)
            if response.status_code == 200:
                print("--------------writing file----------------")
                with open(fname,"w") as f:
                    f.write(response.text)
                print("--------------download successfully-------------")
                return True
        except:
            traceback.print_exc()
        time.sleep(2)   # sleep 2s
        i = i+1
    print("---------------failed to download-----------------")
    return False

def postAndDownload(url,data_json,resultfolder,downloadFileName):
    links = http_post(url,data_json)
    if links:
        datajsonUrl = links[0]
        scenejsonUrl = links[1]
        bool_downloadUrl(datajsonUrl, resultfolder+"\\"+downloadFileName, 25)

def getTestCasesFromcsv(filename):
    testCaseList = []
    with open(filename,'r') as fcsv:
        testCaseList = fcsv.readlines()
        print("---------------number of test cases: ",len(testCaseList)-1,"--------------------")
        if len(testCaseList)<=1:
            return 0

        # remove title bar in csv
        del(testCaseList[0])
        return testCaseList


if __name__ == '__main__':
    # for debug
    # data_json = genPayloadJson(
    #     "empty--d9eeeebb-2626-46dd-b73a-3364dc9c74fd--ori--355ab8b3-1609-4346-8202-1546938d57f2-"+ datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
    #     "d9eeeebb-2626-46dd-b73a-3364dc9c74fd",
    #     "355ab8b3-1609-4346-8202-1546938d57f2",
    #     True,
    #     "")
    # postAndDownload(url,data_json)

    testCaseList = getTestCasesFromcsv(r"D:\A-Flower\AutoStyler\Automation\AutostylerScene\input\823_22.csv")
    resultfolder = os.getcwd()+ "\\result_" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    os.makedirs(resultfolder)
    for each in testCaseList:
        i = 0
        print("-----------Working case: ",i,"#---------------")
        x = each.split(",")
        aliJobId = x[0]+"-"+ datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        designId = x[1].strip("\n")
        templateId = x[2].strip("\n")
        payLoadJson = genPayloadJson(aliJobId,templateId,designId,onlyHardDeco,"")
        postAndDownload(url, payLoadJson, resultfolder, aliJobId+".json")
        i = i+1

    print("All Done!")


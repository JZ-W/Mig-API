#coding = utf-8

# for single test case:
# Step 1: send post request
# Step 2: download dataurl and save to local

import requests
import json
import traceback
import os
import time
import datetime
import threading
import shutil
import ssl
import urllib

tcfile = r"D:\A-Flower\AutoStyler\Automation\AutostylerScene\input\UAT-22.csv"

onlyHardDeco = False
isProd = False
if isProd:
    url = "http://47.95.219.76:30008/api/rest/v1.0/tenants/ezhome/designs/migrate"
else:
    url = "http://123.56.5.77:30008/api/rest/v1.0/tenants/ezhome/designs/migrate"

headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    }


pollingCycle = 3 # try to download file from url every 3s
retryCount = 60 # the retry count for downloading file
# the timeout for each url downloading is 60x3s=180s=3min

downloadFailedTC_1st = [] #files that failed to download for the first cycle
downloadFailedTC_2nd = [] #files that failed to download for the second cycle
requestFailedTC = []

def genPayloadJson(aliJobId,templateId,designId,onlyHardDeco,softAlgorithm):
    values = {
        "aliJobId" : aliJobId,
        "templateId" : templateId,
        "designId" : designId,
        "onlyHardDeco" : onlyHardDeco,
        "softAlgorithm" : "" 
    }
#    print("payload: " + str(values))
    return values

def http_post(url,data_json):
    try:
        print("--------------sending post request ",str(data_json), "-------------")
        jdata = json.dumps(data_json)
        response = requests.post(url, jdata, headers=headers)
        if response.status_code!= 200:
            print("--------------send post request failed ", str(data_json), "-------------")
            requestFailedTC.append(data_json)
            return 0
        hjson = json.loads(response.content)
        if hjson["er"]!= -1:
            print("---------------API failed! ", str(data_json), "-----------------")
            requestFailedTC.append(data_json)
            return 0
        else:
            datajsonUrl = hjson["data"][0]["dataUrl"]
            scenejsonUrl = hjson["data"][0]["sceneUrl"]
        # response.text is str
            return datajsonUrl, scenejsonUrl
    except:
        requestFailedTC.append(data_json)
        traceback.print_exc()

#jsonurl example: https://jr-uat-cms-assets.oss-cn-beijing.aliyuncs.com/Asset/austyler/empty--c5b20a05-a358-4574-a543-7d12a2aa6279--ori--bd05eb67-3817-4ff4-8f3f-f81ea379d556-2018-11-23-14-23-01/data.json
#fname: result folder path and file name
def bool_downloadUrl(jsonurl,fname,pollingCycle,retrycount):
    i = 1
    while i<= retrycount:
        try:
            print("--------------try to download ", i, "/", retrycount, jsonurl)
            # response = requests.get(url)
            # if response.status_code == 200:
            #     print("--------------writing file ", url, "----------------")
            #     with open(fname,"w") as f:
            #         f.writelines(response.text)
            #     print("--------------download successfully ", url, "-------------")
            #     return True
            urllib.request.urlretrieve(jsonurl,fname)
            print("--------------download successfully ", jsonurl, "-------------")
            return True
        except urllib.error.HTTPError as e:
            print("Error code ", e.code)
        except  urllib.error.URLError as e:
            print("Reason ", e.Reason)
        except:
            traceback.print_exc()
            print("--------------download failed ", jsonurl, "-------------")
            downloadFailedTC_1st.append(jsonurl)
        time.sleep(pollingCycle)   # sleep 2s and try to download file again
        i = i+1
    print("---------------failed to download ", jsonurl,"-----------------")
    downloadFailedTC_1st.append(jsonurl)
    return False

def postAndDownload(url,data_json,resultfolder,downloadFileName,pollingCycle,retryCount):
    links = http_post(url,data_json)
    if links:
        datajsonUrl = links[0]
        scenejsonUrl = links[1]
        bool_downloadUrl(datajsonUrl, resultfolder+"\\"+downloadFileName, pollingCycle, retryCount)

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

# generate a tclist for each thread
def assignThread(threadCount,testcaseList):
    totalCaseCount = len(testcaseList)
    tclistForThreads = [] 
    for j in range(threadCount):
        singlethread = []
        for i in range(totalCaseCount):
            if i % threadCount == j:
                singlethread.append(testcaseList[i])
        print("tcNum for this thread: "+str(len(singlethread)))
        tclistForThreads.append(singlethread)
#    print(str(len(tclistForThreads)))
    return tclistForThreads 

#for debug multi thread
def test(eachPayload):
    print('sub thread start!the thread name is:%s    ' % threading.currentThread().getName())
    print(threading.currentThread().getName()+ ": has %s tasks" % len(eachPayload))

def functionForSingleThread(testCaseListForSingleThread):
    print('sub thread start!the thread name is:%s    ' % threading.currentThread().getName())
    WorkingOnCaseNo = 0
    for each in testCaseListForSingleThread:
        print("-----------Working case: ",WorkingOnCaseNo,"#---------------")
        x = each.split(",")
        aliJobId = x[0]+"-"+ datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        designId = x[1].strip("\n")
        templateId = x[2].strip("\n")
        payLoadJson = genPayloadJson(aliJobId,templateId,designId,onlyHardDeco,"")
        postAndDownload(url, payLoadJson, resultfolder, aliJobId+"_data.json",pollingCycle,retryCount)
        WorkingOnCaseNo = WorkingOnCaseNo+1

def getThreadCount(totalCaseCount):
    if totalCaseCount<=30:
        return totalCaseCount
    else:
        return 30

if __name__ == '__main__':
    # for debug
    # data_json = genPayloadJson(
    #     "empty--d9eeeebb-2626-46dd-b73a-3364dc9c74fd--ori--355ab8b3-1609-4346-8202-1546938d57f2-"+ datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
    #     "d9eeeebb-2626-46dd-b73a-3364dc9c74fd",
    #     "355ab8b3-1609-4346-8202-1546938d57f2",
    #     True,
    #     "")
    # postAndDownload(url,data_json)
    tStart = datetime.datetime.now()
    print("-------------Start at " + tStart.strftime('%Y-%m-%d-%H-%M-%S') + ("---------------"))

    testCaseList = getTestCasesFromcsv(tcfile)
    threadCount = getThreadCount(len(testCaseList))
    
    resultfolder = os.getcwd()+ "\\result_" + tStart.strftime('%Y-%m-%d-%H-%M-%S') + "_" + tcfile.split("\\")[-1][:-4]
    os.makedirs(resultfolder)
    
    tclistForThreads = assignThread(threadCount,testCaseList)

    # Start multi threads
    threads = []
    try:
        for i in range(threadCount):
#            print(tclistForThreads[i])
            tmp = []
            tmp.append(tclistForThreads[i])
#            print(tmp)
            th = threading.Thread(target = functionForSingleThread, args = tmp)
            threads.append(th)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    except:
        print("----------Start multi thread failed -----------------------")
        traceback.print_exc()

    tEnd = datetime.datetime.now()
    print("All Done! End at " + tEnd.strftime('%Y-%m-%d-%H-%M-%S') + " Total cost seconds: "+ str((tEnd-tStart).seconds))
    if len(requestFailedTC)>0:
        print(len(requestFailedTC), " cases failed when post request, below are failed cases.")
        print(requestFailedTC)

    if len(downloadFailedTC_1st)>0:
        print(len(downloadFailedTC_1st), " cases failed when download json, below are failed cases.")
        print(downloadFailedTC_1st)

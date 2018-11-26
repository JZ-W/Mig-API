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
datajsonURL = []

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
def assignTC2Thread(threadCount,testcaseList):
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

def postRequestSingleThread(testCaseListForSingleThread):
    print('sub thread start!the thread name is:%s    ' % threading.currentThread().getName())
    WorkingOnCaseNo = 0
    for each in testCaseListForSingleThread:
        print("-----------Working case: ", WorkingOnCaseNo ,"#---------------")
        x = each.split(",")
        aliJobId = x[0]+"-"+ datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        designId = x[1].strip("\n")
        templateId = x[2].strip("\n")
        payLoadJson = genPayloadJson(aliJobId,templateId,designId,onlyHardDeco,"")
        links = http_post(url, payLoadJson)
        if links:
            datajsonURL.append(links[0])
        WorkingOnCaseNo = WorkingOnCaseNo+1

def downloadUrlSingleThread(jsonURLList,resultfolder):
    WorkingOnCaseNo = 0
    for each in jsonURLList:
        fname = resultfolder+"\\"+each.split("/")[-2]+"_"+"data.json"
        bool_downloadUrl(each, fname, pollingCycle, retryCount)
        WorkingOnCaseNo = WorkingOnCaseNo+1

def getThreadCount(totalCaseCount):
    if totalCaseCount<=30:
        return totalCaseCount
    else:
        return 30

if __name__ == '__main__':
    tStart = datetime.datetime.now()
    print("-------------Start at " + tStart.strftime('%Y-%m-%d-%H-%M-%S') + ("---------------"))

    testCaseList = getTestCasesFromcsv(tcfile)
    threadCount = getThreadCount(len(testCaseList))
    
    resultfolder = os.getcwd()+ "\\result_" + tStart.strftime('%Y-%m-%d-%H-%M-%S') + "_" + tcfile.split("\\")[-1][:-4]
    os.makedirs(resultfolder)
    
    tclistForThreads = assignTC2Thread(threadCount,testCaseList)
    threads = []
    try:
        for i in range(threadCount):
            tmp = []
            tmp.append(tclistForThreads[i])
#            print(tmp)
            th = threading.Thread(target = postRequestSingleThread, args = tmp)
            threads.append(th)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    except:
        print("----------Start multi thread for sending request failed -----------------------")
        traceback.print_exc()


    #assign URLs to different threads, and each thread will get a URL list
    datajsonURLForThreads = assignTC2Thread(threadCount,datajsonURL)
    print(datajsonURLForThreads)
   # Start multi threads
    threads = []
    try:
        for i in range(threadCount):
            tmp = []
            tmp.append(datajsonURLForThreads)
#            print(tmp)
            th = threading.Thread(target = downloadUrlSingleThread, args = (datajsonURLForThreads[i],resultfolder))
            threads.append(th)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    except:
        print("----------Start multi thread for downloading failed -----------------------")
        traceback.print_exc()


    if len(requestFailedTC)>0:
        print(len(requestFailedTC), " cases failed when post request, below are failed cases.")
        print(requestFailedTC)

    if len(downloadFailedTC_1st)>0:
        print(len(downloadFailedTC_1st), " cases failed when download json for the 1st cycle.")
        # for each in downloadFailedTC_1st:
        #     if not bool_downloadUrl(each,resultfolder+"\\"+each.split("/")[-2]+"_"+"data.json" , pollingCycle,retryCount):
        #         downloadFailedTC_2nd.append(url)
        threadCount_2nd_download = getThreadCount(len(downloadFailedTC_1st))
        datajsonURLForThreads_2nd = assignTC2Thread(threadCount_2nd_download,downloadFailedTC_1st)
        print(datajsonURLForThreads_2nd)
        # Start multi threads
        threads = []
        try:
            for i in range(threadCount_2nd_download):
                tmp = []
                tmp.append(datajsonURLForThreads_2nd)
                th = threading.Thread(target = downloadUrlSingleThread, args = (datajsonURLForThreads_2nd[i],resultfolder))
                threads.append(th)
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        except:
            print("----------Start multi thread for downloading failed -----------------------")
            traceback.print_exc()


    if len(downloadFailedTC_2nd)>0:
        print(len(downloadFailedTC_2nd), " cases failed when download json, below are failed cases.")
        print(downloadFailedTC_2nd)


    tEnd = datetime.datetime.now()
    print("All Done! End at " + tEnd.strftime('%Y-%m-%d-%H-%M-%S') + " Total cost seconds: "+ str((tEnd-tStart).seconds))
 

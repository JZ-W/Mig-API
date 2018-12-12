#coding = utf-8

import traceback
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import time
import win32gui
import win32con
import os
from PIL import Image


alpha_url = "http://alpha-3d.homestyler.com/?fcdbg=true"
uat_url = "http://uat-3d.homestyler.com/?fcdbg=true"

css_loginframe = '#loginFrame'
css_username = '#__layout > div > div.diy > div.right > div > div > div.sso-box.username > input[type="text"]'
css_password = '#__layout > div > div.diy > div.right > div > div > div.sso-box.password > input[type="password"]'
css_loginbtn = '#__layout > div > div.diy > div.right > div > div > a'
css_welcomeframe = '#welcomediv'

def login(driver):
    time.sleep(5)
    input_loginframe = driver.find_element_by_css_selector(css_loginframe)
    driver.switch_to_frame(input_loginframe)

    input_username = driver.find_element_by_css_selector(css_username)
    input_username.send_keys("tester")
    input_password = driver.find_element_by_css_selector(css_password)
    input_password.send_keys("123456")
    loginbtn = driver.find_element_by_css_selector(css_loginbtn)
    loginbtn.click()
    driver.switch_to.default_content()

    time.sleep(10)
    closewelcomebtn = driver.find_element_by_css_selector('#welcomeframe > div.welcomerightpanel > img.closewelcome')
    closewelcomebtn.click()

def getjsonlist(inputfolder):
    jsonlist = []
    for eachfile in os.listdir(inputfolder):    #eachfile: only filename without folder name
        if eachfile[-5:] == '.json':
            path = os.path.join(inputfolder,eachfile) #path sample: D:\PYS\BulkMigrateAPI\result_2018-12-11-16-16-34.json
            jsonlist.append(path)
    return jsonlist

#jsonpath sample: D:\PYS\BulkMigrateAPI\data.json
def loadsinglejson(driver,jsonpath):
    time.sleep(1)
    debugbtn = driver.find_element_by_css_selector('#floorplannerToolbar > div:nth-child(2) > ul > li:nth-child(31) > span') #hover on debug button
    ActionChains(driver).move_to_element(debugbtn).perform()

    time.sleep(1)
    impexpbtn = driver.find_element_by_css_selector('#floorplannerToolbar > div:nth-child(2) > ul > li:nth-child(31) > ul > li:nth-child(3) > div.tooltext > span.textonly')
    ActionChains(driver).move_to_element(impexpbtn).perform() #hover on import&export menu

    time.sleep(1)
    loadfromlocal = driver.find_element_by_css_selector('#floorplannerToolbar > div:nth-child(2) > ul > li:nth-child(31) > ul > li:nth-child(3) > ul > li:nth-child(2) > div > span.textonly')
    loadfromlocal.click()  #click on load from local button

    time.sleep(2)
    #win32gui
    dialog = win32gui.FindWindow('#32770',u'打开')
    print('dialog', dialog)
    ComboBoxEx32 = win32gui.FindWindowEx(dialog, 0, 'ComboBoxEx32', None) 
    print('ComboBoxEx32')
    ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, 'ComboBox', None)
    print('ComboBox')
    edit = win32gui.FindWindowEx(ComboBox, 0,'Edit',None)
    print('edit')
    enterkey = win32gui.FindWindowEx(dialog,0,'Button',u'打开(&O)')
    print('enterkey')

    time.sleep(1)
    print(win32gui.SendMessage(edit, win32con.WM_SETTEXT, None, jsonpath)) # 往输入框输入绝对地址
    time.sleep(1)
    print(win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, enterkey)) # 按button
    time.sleep(15)

#resultfolder sample: D:\PYS\BulkMigrateAPI\temp
#picname sample: a.png
def takesnap(driver,resultfolder,picname):
    driver.save_screenshot(resultfolder +'\\'+ picname)
    picture = Image.open(resultfolder +'\\'+ picname)
    canvasBox = (60,100,1126,718) #canvasBox是一个四元组 限定所述左，上，右，和下像素坐标参数,the cropped image size is 1066x618
    picture = picture.crop(canvasBox)
    picture.save(resultfolder +'\\'+ picname)


if __name__ == '__main__':
    
    tStart = datetime.datetime.now()
    sStart = tStart.strftime('%Y-%m-%d-%H-%M-%S')
    print("---------starting ", sStart ,"-----------")

    inputfolder = r'D:\PYS\BulkMigrateAPI\result_2018-12-12-09-35-48_sampleRoom_68'
    jsonlist = getjsonlist(inputfolder)
    if len(jsonlist) == 0:
        print('-------------no json file------------------')
    else:
        chromedriver = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        driver = webdriver.Chrome(chromedriver)
#        driver.maximize_window()
#        driver.set_window_rect(x=10, y=10) #Sets the x, y coordinates of the window
        driver.set_window_size(1400,850) 
        print(driver.get_window_size)
        driver.implicitly_wait(25)
        driver.get(uat_url)
        print(driver.title)

        login(driver)
        
        snapshotsfolder = inputfolder+'\\snapshots_'+sStart
        os.makedirs(snapshotsfolder)
        print('------------', len(jsonlist), ' json to be uploaded------------')
        workingNo = 0
        for each in jsonlist:
            print('------------working on ',workingNo, '# json----------')
            print('----------uploading',each)
            loadsinglejson(driver,each)

            print('----------taking snapshots',each)
            picname = each.split('\\')[-1][:-5] + '.png' #get json file name as picname
            takesnap(driver,snapshotsfolder,picname)
            workingNo = workingNo+1
    
        driver.quit()
    tEnd = datetime.datetime.now()
    print("All Done! End at " + tEnd.strftime('%Y-%m-%d-%H-%M-%S') + " Total cost seconds: "+ str((tEnd-tStart).seconds))


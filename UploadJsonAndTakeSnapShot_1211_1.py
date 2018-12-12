#coding = utf-8

import traceback
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import time
import win32gui
import win32con

print("---------Uploading-----------")
chromedriver = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
driver = webdriver.Chrome(chromedriver)
driver.set_window_size(1400,800)
driver.implicitly_wait(25)
url="http://alpha-3d.homestyler.com/?fcdbg=true"
driver.get(url)
print(driver.title)

css_loginframe = '#loginFrame'
css_username = '#__layout > div > div.diy > div.right > div > div > div.sso-box.username > input[type="text"]'
css_password = '#__layout > div > div.diy > div.right > div > div > div.sso-box.password > input[type="password"]'
css_loginbtn = '#__layout > div > div.diy > div.right > div > div > a'
css_welcomeframe = '#welcomediv'

time.sleep(3)
input_loginframe = driver.find_element_by_css_selector(css_loginframe)
driver.switch_to_frame(input_loginframe)

input_username = driver.find_element_by_css_selector(css_username)
input_username.send_keys("tester")
input_password = driver.find_element_by_css_selector(css_password)
input_password.send_keys("123456")
loginbtn = driver.find_element_by_css_selector(css_loginbtn)
loginbtn.click()
driver.switch_to.default_content()

time.sleep(7)
closewelcomebtn = driver.find_element_by_css_selector('#welcomeframe > div.welcomerightpanel > img.closewelcome')
closewelcomebtn.click()

time.sleep(1)
debugbtn = driver.find_element_by_css_selector('#floorplannerToolbar > div:nth-child(2) > ul > li:nth-child(31) > span')
ActionChains(driver).move_to_element(debugbtn).perform()

time.sleep(1)
impexpbtn = driver.find_element_by_css_selector('#floorplannerToolbar > div:nth-child(2) > ul > li:nth-child(31) > ul > li:nth-child(3) > div.tooltext > span.textonly')
ActionChains(driver).move_to_element(impexpbtn).perform()

time.sleep(1)
loadfromlocal = driver.find_element_by_css_selector('#floorplannerToolbar > div:nth-child(2) > ul > li:nth-child(31) > ul > li:nth-child(3) > ul > li:nth-child(2) > div > span.textonly')
loadfromlocal.click()


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
print(win32gui.SendMessage(edit, win32con.WM_SETTEXT, None, r'D:\PYS\BulkMigrateAPI\empty--8e6499e4-6574-4f18-aef2-4308583ae6e8--ori--989b3cd2-4c13-463d-bac5-2cb927070bb3-2018-11-28-17-27-21.json')) # 往输入框输入绝对地址
time.sleep(1)
print(win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, enterkey)) # 按button

time.sleep(15)
screenpath = r'D:\PYS\BulkMigrateAPI\temp'
tStart = datetime.datetime.now()
sStart = tStart.strftime('%Y-%m-%d-%H-%M-%S')
driver.save_screenshot(screenpath +'\\'+ sStart +'.png')

print('Done')

#driver.quit()





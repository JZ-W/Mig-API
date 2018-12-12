#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import traceback
from PIL import Image
from operator import sub
import PIL
import re

'''
input:
latestimg, baseimg: 2 images to be compared
designname: user defined diff image name
diff_dir: directory to save diff image

output:
1. return diff percentage(float)
2. save diff image in diff_dir,filename:$designname+'__diff.jpg'
'''
def CompareTwoImage(latestimg, baseimg,designname,diff_dir):
    try:
        im2=Image.open(latestimg)
        im1=Image.open(baseimg)
        diffcount = 0.0

        diffimg=Image.new('RGB',im1.size,"black")
        pixels=diffimg.load()
                    
        im2pixori=im2.load()
        im1pixori=im1.load()
        for i in range (0, im2.size[0]):
            for j in range(0,im2.size[1]):
                #print i,j
                if len(im2pixori[i,j])==4:
                    im2pix=im2pixori[i,j][0:3]
                else:
                    im2pix=im2pixori[i,j]
                if len(im1pixori[i,j])==4:
                    im1pix=im1pixori[i,j][0:3]
                else:
                    im1pix=im1pixori[i,j]
                is_both_transparent= (len(im1pixori[i,j])==4 and len(im2pixori[i,j])==4 and im2pixori[i,j][3]==0 and im1pixori[i,j][3]==0)
                is_one_transparent1=((len(im1pixori[i,j])==4 and len(im2pixori[i,j])==3 and im1pixori[i,j][3]!=255) or (len(im1pixori[i,j])==3 and len(im2pixori[i,j])==4 and im2pixori[i,j][3]!=255)) 
                is_one_transparent2=(len(im1pixori[i,j])==4 and len(im2pixori[i,j])==4) and ( (im1pixori[i,j][3]==0 and im2pixori[i,j][3]!=0)or (im1pixori[i,j][3]!=0 and im2pixori[i,j][3]==0))
                is_one_transparent= is_one_transparent1 or is_one_transparent2
                    
                
                seq=tuple(map(sub,im1pix,im2pix))
                if is_both_transparent:
                    pass
                elif is_one_transparent:
                    diffcount = diffcount + 1.0
                    pixels[i,j]=(255,0,0)  
                elif (abs(seq[0]) >30 or abs(seq[1]) >30 or abs(seq[2])>30 ):
                    diffcount = diffcount + 1.0
                    pixels[i,j]=(255,0,0)            
        diffImgLen = im2.size[0] * im2.size[1] * 1.0
        diffpercent = (diffcount * 100) / diffImgLen
        if baseimg.endswith(".png"):
            diffImage=diff_dir+'\\'+designname+'__diff.png'
        if not os.path.exists(diff_dir):
            os.makedirs(diff_dir)
        diffimg.save(diffImage)
#        print("diff percentage:",str(round(diffpercent,2))+"%")
        return round(diffpercent,2)
    except IOError as e:
        err_str=str(e)
        if "cannot identify image file" in err_str:
            err_str=re.sub('./result(.+)/(.+)',r'\2',err_str) 
            print(err_str)
        traceback.print_exc()
        raise Exception(err_str)
          



def test():
    baseimg=r"D:\PYS\BulkMigrateAPI\result_2018-12-11-16-16-34_UAT-30\snapshots_2018-12-12-13-59-27\ori--4ce11bbe-4c39-44a1-965f-ac8b4df7aa12--empty--76c24ea9-9e00-4533-9618-a39124ec9ad0-2018-12-11-16-16-34_data.png"
    latestimg=r"D:\PYS\BulkMigrateAPI\result_2018-12-11-16-16-34_UAT-30\snapshots_2018-12-12-14-11-37\ori--02d24956-8b27-485b-806d-46629fbe8e48--empty--747972db-b48a-43db-af7e-4d2d5fec6b81-2018-12-11-16-16-34_data.png"
    designname="xy"
    diff_dir=r"D:\PYS\BulkMigrateAPI\result_2018-12-11-16-16-34_UAT-30\snapshots"
    CompareTwoImage(latestimg, baseimg,designname,diff_dir)

def compareTwoFolder(baseFolder,latestFolder,diffDir):
    baselist = os.listdir(baseFolder)
    latestlist = os.listdir(latestFolder)
    for eachbase in baselist:
        if not eachbase.endswith('.png'):
            baselist.remove(eachbase)
    for eachlatest in latestlist:
        if not eachlatest.endswith('.png'):
            latestlist.remove(eachlatest)
    for eachlatest in latestlist:
        latestdesignname = eachlatest[:-29] #get tcname without timestamp, sample: ori--02d24956-8b27-485b-806d-46629fbe8e48--empty--747972db-b48a-43db-af7e-4d2d5fec6b81
        boolFindbase = False
        for eachbase in baselist:
            if eachbase.startswith(latestdesignname):
                baseimage = os.path.join(baseFolder,eachbase)
                latestimage = os.path.join(latestFolder,eachlatest)
                diffper = CompareTwoImage(latestimage,baseimage,latestdesignname,diffDir)
                print(latestdesignname, ' : ',diffper)
                boolFindbase = True    
        if not boolFindbase:       
            print(latestdesignname, ': no baseline')
    
   
if __name__ == "__main__":
    basefolder = r'D:\PYS\BulkMigrateAPI\result_2018-12-12-09-47-06_PROD-22-baseline\snapshots_2018-12-12-16-27-49'
    latestfolder = r'D:\PYS\BulkMigrateAPI\result_2018-12-07-12-30-12_PROD-22\snapshots_2018-12-12-16-48-06'
    diff_dir = r'D:\PYS\BulkMigrateAPI\temp'
    compareTwoFolder(basefolder,latestfolder,diff_dir)
# -*- coding: utf-8 -*-

import selenium
from selenium import webdriver
import contextlib
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
import string
import time
import sys
reload(sys)
import os
import random
import shutil
from bs4 import BeautifulSoup
import urllib2
import urllib
import datetime
import re
import os.path
import requests
import subprocess
import math
sys.setdefaultencoding('Cp1252')

big_path="/tmp/"
accounts = ["test@domain.com"]
password = "your_password"
video_server_login = "https://www.xvideos.com/account"
video_server_upload = "https://www.xvideos.com/account/uploads/new"
urls = ['https://www.xvideos.com/video8342259/xxxxxxxxxxxxxxxxxxxxxxx']

length_regexp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
re_length = re.compile(length_regexp)


browser = selenium.webdriver.Chrome("chromedriver")

wait = ui.WebDriverWait(browser,60*20)

def Login(username,password):

    browser.get('http://upload.xvideos.com/account')

    time.sleep(2)

    browser.find_element_by_id('signin-form_login').send_keys(username)

    browser.find_element_by_id('signin-form_password').send_keys(password)

    time.sleep(2)

    browser.find_element_by_xpath("//div[@class='col-sm-offset-4 col-sm-8'][1]/button[@class='btn btn-danger btn-lg'][1]").click()

    time.sleep(3)

    print "Sucessfull login"



def Upload(tags, myvideo):
    print "Begin upload video"
    browser.get('http://upload.xvideos.com/account/uploads/new')

    print "Get upload page OK"
    time.sleep(3)
    
    browser.find_element_by_id("upload_form_category_category_centered_category_straight").click()
    print "Checked: Straight"

    time.sleep(2)

    browser.find_element_by_id("upload_form_titledesc_title").send_keys("My first do this")
    print "File description: OK"
    time.sleep(2)
    browser.find_element_by_id("upload_form_titledesc_title_network").send_keys("My first time upload: a couple in warm")
    print "File description Network: OK"
    time.sleep(2)
    
    tagbtn = browser.find_element_by_xpath("//button[@class='add'][1]")
    browser.execute_script("arguments[0].click();", tagbtn, tags)
    tagbtn.click()
    count = 0
    for tag in tags:
    	count = count + 1
    	if (count <= 20):
        	browser.find_element_by_xpath("//div[@class='tag-list'][1]//input[1]").send_keys(tag)
        	tagbtn.click()

    print "Set Tag OK"
    time.sleep(2)
        
    element = browser.find_element_by_id("upload_form_file_terms")
    browser.execute_script("arguments[0].click();", element)
    print "Term: OK"
    time.sleep(2)
    

    upload =browser.find_element_by_id('upload_form_file_file_options_file_1_file')

    upload.send_keys(str(myvideo))
    upload.submit()

    time.sleep(2)


def split_by_part(input_path, output_path):
    output = subprocess.Popen("ffmpeg -i '"+input_path+"' 2>&1 | grep 'Duration'",
                            shell = True,
                            stdout = subprocess.PIPE
                            ).stdout.read()
    print output
    print input_path
    matches = re_length.search(output)
    if matches:
        video_length = int(matches.group(1)) * 3600 + \
                        int(matches.group(2)) * 60 + \
                        int(matches.group(3))
        print "Video length in seconds: "+str(video_length)
    else:
        print "Can't determine video length."
        raise SystemExit
    
    split_second = int(math.ceil(video_length/3))
    split_cmd = "ffmpeg -i '%s' -c copy -map 0 -segment_time %s -f segment %s" % (input_path, str(split_second), output_path)
    output = subprocess.Popen(split_cmd, shell = True, stdout = subprocess.PIPE).stdout.read()
    print output
        
def log_website():
    time1=datetime.datetime.now()
    
    url = video_server_login
    values = {'signin-form[login]': 'test@mail.com',
          'signin-form[password]': 'password'}
    r = requests.post(url, data=values)
    print r.status_code
    
    file_upload = big_path +"output_video02.mp4"
    filehandle = open(file_upload)
    url2=video_server_upload
    r2 = requests.post(url2, data={},files = {'upload':filehandle})
    print r2.text


def save_file(this_download_url,path = big_path+str(datetime.datetime.now())[:-7]+".mp4"):
    print"- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - "
    time1=datetime.datetime.now()
    print str(time1)[:-7],
    if (os.path.isfile(path)):
        file_size=os.path.getsize(path)/1024/1024
        print "File "+path+" ("+ str(file_size)+"Mb) already exists."
        return
    else:
        
        f = urllib2.urlopen(this_download_url)
        data = f.read()
        with open(path, "wb") as code:
            print "loading"
            code.write(data)
        time2=datetime.datetime.now()
        print str(time2)[:-7],
        print path+" Done."
        use_time=time2-time1
        print "Time used: "+str(use_time)[:-7]+", ",
        file_size=os.path.getsize(path)/1024/1024
        print "File size: "+str(file_size)+" MB, Speed: "+str(file_size/(use_time.total_seconds()))[:4]+"MB/s"
        output_path = big_path + "output_video%02d.mp4"
        split_by_part(path, output_path)
    
def download_the_av(url):
    req = urllib2.Request(url)
    content = urllib2.urlopen(req).read()
    while len(content)<100:
        print"try again..."
        content = urllib2.urlopen(req).read()
	

    print "Web page length :" +str(len(content))
    titleRe = "setVideoTitle\(\'(.+?)\'\);"
    lowUrlRe = "setVideoUrlHigh\(\'(.+?)\'\);"
    patternTitle = re.compile(titleRe)
    patternLowUrl = re.compile(lowUrlRe)
    to_find = content
    matchTitle = patternTitle.search(to_find)
    matchLowUrl = patternLowUrl.search(to_find)
    soup = BeautifulSoup(to_find, "html.parser")
    video_tags = soup.find("meta", {"name":"keywords"})['content']
    print "tags = " + video_tags

    if matchTitle:
        title = matchTitle.group(1)+".mp4"
        print "Film title " + title

    if matchLowUrl:
        lowUrl = matchLowUrl.group(1)
        print lowUrl
    if len(lowUrl)>0:
        save_file(lowUrl)


    return video_tags.split(",")

def video_login_upload(tags_upload):

    for acc in accounts:

        try:

            browser.get("http://upload.xvideos.com/account/signout")

        except:

            Exception

        browser.delete_all_cookies()

        print "Login"
        Login(acc ,password)
        file_upload = big_path +"output_video02.mp4"
        rtrn = Upload(tags_upload, file_upload)


for url in urls:
    tags_upload = download_the_av(url)
    video_login_upload(tags_upload)




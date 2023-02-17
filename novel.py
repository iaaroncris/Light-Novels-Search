from os import link
import requests
import threading
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from huepy import *
from PIL import Image
import urllib.request
import json
import ast
import re

ua = UserAgent()
user_agent = ua.random
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--headless")
options.add_argument("user-agent=" + user_agent)
driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
filepath = "E:/Code and Projects/Output/LNSearch Data/"

#To find novel names and links
def update_link_db():

    data = requests.get("http://www.vn-meido.com/k1/index.php?topic=3084.0")
    soup = BeautifulSoup(data.content, "html.parser")
    links = soup.findAll(class_='bbc_link', href=True)
    texts = soup.findAll('a', attrs={'class':'bbc_link'})
    all_texts = []
    all_links = []
    for item in texts:
        temp = item.get_text()
        item = re.sub(r"\{\w+\}\s","",temp)
        temp = re.sub(r'\'',u'\u2019',item)
        temp = temp.lower()
        all_texts.append(temp)
    for item in links:
        all_links.append(item['href'])
    dictionary = dict(zip(all_texts, all_links))
    with open('LinksDB.txt','w+') as file:
        file.write(json.dumps(dictionary))
    file.close()

#To find alternative English names
def update_eng_name_db():
   
    data = requests.get("http://www.vn-meido.com/k1/index.php?topic=3084.0")
    soup = BeautifulSoup(data.content, "html.parser")
    texts = soup.find_all('a', attrs={'class':'bbc_link'})
    all_texts_eng = []
    all_texts = []
    for a_tag in texts:
        temp1 = a_tag.get_text()
        try:
            temp = a_tag.next_sibling.get_text()
        except:
            pass
        if(temp!=" "):
            text = re.sub(r'[\({}\)]',"",temp)
            text = re.sub(r'^\s',"",text)
            item = re.sub(r"\{\w+\}\s","",temp1)
            text = text.lower()
            item = item.lower()
            all_texts_eng.append(text)
            all_texts.append(item)
    dictionary = dict(zip(all_texts_eng, all_texts))
    with open('EngLinksDB.txt','w+') as file:
        file.write(json.dumps(dictionary))
    file.close()

#To retrieve novel link
def find_download_link():
    flag = 0
    with open('LinksDB.txt') as f:
        data = f.read()
    link = ast.literal_eval(data)

    with open('EngLinksDB.txt') as file:
        list = file.read()
    name = ast.literal_eval(list)
    
    for k in associate_name:
        if k.lower() in link:
            flag = 1
            k = k.lower()
            print(good(bold(under(orange("Download Link:")))))
            print(bad(under(purple(link[k])))) 

    if(flag == 0):
        for j in associate_name:
            if j.lower() in name:
                flag = 2
                j = j.lower()
                key = name[j]
                print(good(bold(under(orange("Download Link:")))))
                print(bad(under(purple(link[key]))))
    if(flag == 0):
        print(run(bold(orange("Novel does not have downloadable file"))))
        
    f.close()
    file.close()
    driver.quit()

#To search for the Novel
print('\n\n=============Novel Finder=============')
# def novel_directory():
seriesName = input(lightgreen("\nEnter series name:- "))
finalName = seriesName.replace(' ', '+')
driver.get(f'https://www.novelupdates.com/?s={finalName}&post_type=seriesplans')

#Show the titles
stitle = driver.find_elements(By.CSS_SELECTOR, "div.search_title a")
series_name = []
for elem in stitle:
    series_name.append(elem.text)
    
counter = 0
for item in series_name:
    print(cyan(f"{counter + 1}. {item}"))
    counter = counter + 1

if(counter == 0):
    print("No such novel found")
    driver.quit()
    exit()
choice = input(lightgreen("\n\nChoose the series:- "))
series_title = stitle[int(choice) - 1]
series_title.click()

#Title
print("\n\n")
print(good(bold(under(orange("Title")))))
title = driver.find_element(By.CLASS_NAME, "seriestitlenu").text
print (info(bold(red(title)))+"\n")

#Series Cover
coverImage = driver.find_element(By.CSS_SELECTOR, "div.seriesimg img").get_attribute('src')
coverImageName = coverImage.split('/')[-1]
if(coverImageName.casefold() != 'noimagefound.jpg'):
    urllib.request.urlretrieve(coverImage,coverImageName)
    #Show Image
    im = Image.open(coverImageName)
    ImagePath = f'{filepath}'+f'{coverImageName}'
    im = im.convert('RGB')
    im.save(f'{ImagePath}','jpeg')
    im.show(f"{ImagePath}")

#Description
print(good(bold(under(orange("Description")))))
description = driver.find_element(By.ID, "editdescription").text
print(info(bold(red(description+"\n"))))

#Genre
print(good(bold(under(orange("Genre")))))
genre = driver.find_element(By.ID, "seriesgenre").text
print(info(bold(red(genre)))+"\n")

#Associated Names
print(good(bold(under(orange("Associate Name")))))
associateName = driver.find_element(By.ID, "editassociated").text
print(info(bold(red(associateName)))+"\n")
associate_name = []
temp = []
temp = associateName.split('\n')
for item in temp:
    sub = re.sub(r"\s\(\w+\)","",item)
    associate_name.append(sub)
item = re.sub(r"\s\(\w+\)","",title)
associate_name.append(item)
    
#Status in COO
print(good(bold(under(orange("Status COO")))))
statusCoo = driver.find_element(By.ID, "editstatus").text
print(info(bold(red(statusCoo)))+"\n")

#Licensed
print(good(bold(under(orange("Licensed")))))
licensed = driver.find_element(By.ID, "showlicensed").text
print(info(bold(red(licensed)))+"\n")
#English Publisher
if(licensed.casefold()=="yes"):
    print(good(bold(under(orange("English Publisher")))))
    englishPublisher = driver.find_element(By.ID, "showepublisher").text
    print(info(bold(red(englishPublisher)))+"\n")

#Completed Translated
print(good(bold(under(orange("Completely Translated")))))
translated = driver.find_element(By.ID, "showtranslated").text
print(info(bold(red(translated)))+"\n")

#To download link
choice = input(bold(lightgreen("Do you want to check if you can download this book?(Y/N):-")))
if (choice.lower()=='y'):
    update_link_db()
    update_eng_name_db()
    find_download_link()

#Multithreading
if __name__ == "__main__":
    t2 = threading.Thread(target=update_link_db,name='t2')
    t3 = threading.Thread(target=update_eng_name_db, name='t3')
    
    t2.start()
    t3.start()

    t2.join()
    t3.join()


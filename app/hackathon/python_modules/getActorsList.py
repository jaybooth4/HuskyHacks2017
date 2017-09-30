import concurrent.futures
import sys, traceback
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from pprint import pprint
import csv


#Traceback template for properly printing exceptions
traceback_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s\n'''

driver = webdriver.Chrome('chromedriver')
driver.get("http://www.imdb.com/chart/moviemeter?ref_=nv_mv_mpm_8")
driver.implicitly_wait(10)

#actorsWriter = csv.writer(actorsFile)

actorsDict = eval(open('actorsDict.txt', 'r').read())


titles =[]
for title in driver.find_elements_by_class_name('titleColumn'):
    titles.append(title.find_element_by_tag_name('a').get_attribute('href'))
pprint (titles)

for url in titles:
    print str(url)
    driver.get(str(url))
    actors = driver.find_elements_by_css_selector("[itemprop='actor']")
    for actor in actors:
        link = actor.find_element_by_css_selector("a[itemprop='url']")
        actorsDict[actor.text] = link.get_attribute('href')
    print len(actors)

actorsFile = open("actorsDict.txt", "r+")
actorsFile.write(str(actorsDict))
    # print "============================="
    # for actor in allActorsList:
    #     actorlink = actor.find_element_by_class_name("itemprop").find_element_by_tag_name('a')
    #     driver.execute_script("arguments[0].setAttribute('style', 'border-style: solid; border-color: lightgreen')", actorlink)

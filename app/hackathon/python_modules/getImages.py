import concurrent.futures
import sys, traceback
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from pprint import pprint
import urllib


actorsDict = eval(open('actorsDict.txt', 'r').read())

#Traceback template for properly printing exceptions
traceback_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s\n'''

def printTraceback():
    traceback_details = {
                        'filename': sys.exc_info()[2].tb_frame.f_code.co_filename,
                        'lineno'  : sys.exc_info()[2].tb_lineno,
                        'name'    : sys.exc_info()[2].tb_frame.f_code.co_name,
                        'type'    : sys.exc_info()[0].__name__,
                        'message' : sys.exc_info()[1].message
    }
    print traceback_template % traceback_details

class scraper:

    def __init__(self):
        print "Making Scraper"
        self.driver = webdriver.Chrome('chromedriver')
        self.driver.implicitly_wait(10)

    def downloadImage(self, url, name):
        urllib.urlretrieve(url, "pictures/%s.jpg" % name)

    def outlineElementAsGreen(self, element):
        self.driver.execute_script("arguments[0].setAttribute('style', 'border-style: solid; border-color: lightgreen; border-width: 5px')", element)

    def loadPage(self, url):
        self.driver.get(url)

    def getName(self):
        return self.driver.find_element_by_css_selector("span[itemprop='name']").text

    def getPicture(self):
        try:
            return self.driver.find_element_by_id('name-poster')
        except Exception as exc:
            print exc
            return None

    def getPictureSrc(self, picture):
        return picture.get_attribute('src')

    def scrapeActor(self, url):
        self.loadPage(url)
        name = self.getName()
        picture = self.getPicture()
        if picture != None:
            self.outlineElementAsGreen(picture)
            self.downloadImage(self.getPictureSrc(picture), name)
        return name

    def nuke(self):
        self.driver.quit()

def downloadImage(url, name):
    urllib.urlretrieve(url, "pictures/%s.jpg" % name)

def outlineElementAsGreen(thisDriver, element):
    thisDriver.execute_script("arguments[0].setAttribute('style', 'border-style: solid; border-color: lightgreen; border-width: 5px')", picture)

windowSize = 10

scraperStack = []
for i in range(0, windowSize):
    print "constructing scraper"
    scraperStack.append(scraper())

def runScrape(url, scraperStack):
    scraper = scraperStack.pop()
    try:
        name = scraper.scrapeActor(url)
    except Exception as exc:
        print exc
        printTraceback()
        scraperStack.append(scraper)
        return "Error"
    else:
        scraperStack.append(scraper)
        return name

executor = concurrent.futures.ThreadPoolExecutor(max_workers=windowSize)
futures = {}
for actor in actorsDict.keys():
    futures[executor.submit(runScrape, actorsDict[actor], scraperStack)] = url

totalRuns = len(futures)
print str(totalRuns) + " futures loaded."

runCount = 0
for future in concurrent.futures.as_completed(futures):
    url = futures[future]
    try:
        result = future.result()
    except Exception as exc:
        print str(runCount) + "/" + str(totalRuns) + url + ' generated an exception!'
        printTraceback()
    else:
        print str(runCount) + "/" + str(totalRuns) + " - " + result + " completed."
    runCount += 1

for scraper in scraperStack:
    scraper.nuke()

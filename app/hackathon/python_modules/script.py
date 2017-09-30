'''
Created on August 30, 2017

@author: connifm

To run script enter system arguments in this order after script name:
1- Number of Runs
2- Number of Selenium Instances to run in parallel
3- Name of CSV output file
4- Environment to run on (prod or gamma)

Example:

python UI_Dashboard_Test.py 10 5 output.csv prod

Runs script 10 times, with 5 windows, outputs to output.csv, on prod
'''

import time
import concurrent.futures
from datetime import datetime
import timeit
import csv
import re
import sys, traceback
import logging
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from browsermobproxy import Server

from selenium.webdriver.common.by import By

#Traceback template for properly printing exceptions
traceback_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s\n'''

class component:
     def __init__(self, name, xpath, flag):
         self.name = name
         self.xpath = xpath
         self.flag = flag

class FlagError(StandardError):
    def __init__(self, arg):
        self.strerror = arg
        self.args = {arg}

def printTraceback():
    traceback_details = {
                        'filename': sys.exc_info()[2].tb_frame.f_code.co_filename,
                        'lineno'  : sys.exc_info()[2].tb_lineno,
                        'name'    : sys.exc_info()[2].tb_frame.f_code.co_name,
                        'type'    : sys.exc_info()[0].__name__,
                        'message' : sys.exc_info()[1].message
    }
    print traceback_template % traceback_details

'''
 Dictionary of components to scan page for
 ** ANY FLAGS SHOULD HAVE A PROPER NAME TO ACCURATELY LOG THEM
'''
components = [
                        component('pick', "//*[@id=\"PICK\"]/div[2]/ar-kpi-summary-instance/div/section/div/div[1]/span", False),
                        component('stow', "//*[@id=\"STOW\"]/div[2]/ar-kpi-summary-instance/div/section/div/div[1]/span", False),
                        component('simpleBinCount', "//*[@id=\"COUNT\"]/div[2]/ar-kpi-summary-instance[1]/div/section/ul/li/div/div[2]/p[2]/span/span", False),
                        component('cycleCount', "//*[@id=\"COUNT\"]/div[2]/ar-kpi-summary-instance[2]/div/section/ul/li/div/div[2]/p[2]/span/span", False),
                        component('simpleRecordCount', "//*[@id=\"COUNT\"]/div[2]/ar-kpi-summary-instance[3]/div/section/ul/li/div/div[2]/p[2]/span/span", False),
                        component('machRateGraph', "/html/body/ui-view/ar-navigation/div/ui-view/div/div/div[2]/div/div[3]/div/div/div/div/div[1]/div[1]/ar-chart/div/table/tbody/tr/td[1]/span", False),
                        component('taktTimeGraph', "/html/body/ui-view/ar-navigation/div/ui-view/div/div/div[2]/div/div[3]/div/div/div/div/div[1]/div[2]/ar-chart/div/table/tbody/tr/td[1]/span", False),
                        component('bottomTable', "//*[@id=\"2962\"]/div[2]/table/tbody/tr[1]/td[1]/span", False)
                    ]



#List of buildings to test
BDGS = ['BFI4', 'BWI2', 'EWR4', 'LTN4', 'MKE1', 'OAK4', 'TPA1', 'MAN1', 'WRO3', 'HND6', 'DFW7', 'BDL2', 'MSP1', 'YYZ4']

#URL Map
URLS = {'prod' : "https://roboscout.amazon.com/ui/dashboard/buildingPerformance?sites=(%s)",
        'gamma' : "https://roboscoutgamma-pdx.corp.amazon.com/ui/dashboard/buildingPerformance?sites=(%s)"}

#System Arguments read in from command line
numOfRuns = int(sys.argv[1])    #number of times to test each building in BDGS
windowSize = int(sys.argv[2])   #number of parallel selenium windows you want
windowLimit = 7                 #Set max parallel selenium window
outfile = sys.argv[3]           #CSV to output to
env = sys.argv[4]               #env to test on (prod or gamma)

#VERIFY INPUTS:
if (windowSize > windowLimit):  #Check if requested windowSize is too big
    print "ERROR: Window Size Too Large!!"
    exit()

if not URLS.has_key(str(env)):  #Check if env is valid
    print "ERROR: Bad Env Input!!"
    print env
    exit()

#Open output file to append to and init csvWriter
csvOutFile = open(outfile, 'a')
csvWriter = csv.writer(csvOutFile)


#Tester class - holds its own instance of a selenium webdriver used to scan and time a page.
class tester:

    def __init__(self):
        self.driver = webdriver.Chrome('chromedriver') #instance of selenium webdriver
        self.componentTimes = {} #component time map for saving and logging timing data

    #Method used to record load times from ajaxStartTime to the moment they are loaded
    #ajaxStartTime - start time of timing
    #building - building being currently tested
    #metrics - map of metrics to scan far
    def pollForMetrics(self, ajaxStartTime, building, metrics, flagCount):
        for metric in metrics:  #for each metric given
            if self.componentTimes.get(metric.name, None) == None: #if a time is not already recorded
                try:
                    element = self.driver.find_element_by_xpath(metric.xpath) #find element on page
                    value = element.text
                except:
                    pass
                else:
                    # TODO: ADD 'NO DATA' INTELLIGENCE HERE
                    if value != "": #if the value is not blank
                        self.componentTimes[metric.name] = round((datetime.now() - ajaxStartTime).total_seconds(), 3) #log time
                        #wrap component in green border when found and logged
                        self.driver.execute_script("arguments[0].setAttribute('style', 'border-style: solid; border-color: lightgreen')", element)
                        if metric.flag:
                            raise FlagError(metric.name)
                    else:   #if value is blank
                        #wrap component in red border
                        self.driver.execute_script("arguments[0].setAttribute('style', 'border-style: solid; border-color: red')", element)

        if len(self.componentTimes) == (len(metrics) - flagCount):    #if every component has a recorded time
            return True
        else:
            return False

    def loadPage(self, url, building, metrics, flagCount):
        self.componentTimes.clear() #empty previously recorded times
        # TODO: Add inital load failure logic here
        pageLoadStart=datetime.now()
        self.driver.get(url)
        pageLoadEnd=datetime.now()
        initLoad = (pageLoadEnd - pageLoadStart).total_seconds() #record page response time
        if self.driver.find_element_by_xpath('/html/head/title').text != "Roboscout":
            print "Roboscout did not load correctly!"
            passed = False
            failureType = self.driver.find_element_by_xpath('/html/body/h1').text
        else:
            try:
                #continuously poll page for given metrics until all metrics are found, or 45 seconds has passed
                WebDriverWait(self.driver, 45).until(lambda poller: self.pollForMetrics(pageLoadEnd, building, metrics, flagCount))
            except TimeoutException as exc:
                print building
                printTraceback()
                passed = False
                failureType = "AJAX Timeout"
            except FlagError as exc:
                print building
                printTraceback()
                passed = False
                failureType = exc
            except Exception as exc:
                print building
                printTraceback()
                return []
            else:
                passed = True
                failureType = None
        result = [pageLoadStart, building, passed]
        for metric in metrics:
            if not metric.flag:
                result.append(self.componentTimes.get(metric.name, None))
        result.extend([initLoad, env, failureType])

        return result

    #closes selenium webdriver instance
    def nuke(self):
        self.driver.quit()

#method used to launch new test
#url - url to test
#building - building being currently tested
#testerStack - stack of tester instances to be used
#metrics - map of metrics to record times of
def runTest(url, building, testerStack, metrics, flagCount):
    tester = testerStack.pop() #get tester of stack to be used for this test
    try:
        result = tester.loadPage(url, building, metrics, flagCount) # run test
    except Exception as exc:
        print exc
        printTraceback()
        testerStack.append(tester)
        return []
    else:
        testerStack.append(tester)
        return result

# server = Server("/Users/connifm/Roboscout/browsermob-proxy-2.1.4/bin/browsermob-proxy")
# server.start()
# proxy = server.create_proxy()

#Builds stack of testers to be reused for testing
testerStack = []
for i in range(0, windowSize):
    testerStack.append(tester())

#Calculate flagCount
flagCount = 0
for component in components:
    flagCount = flagCount + component.flag

#executor used to queue up futures
executor = concurrent.futures.ThreadPoolExecutor(max_workers=windowSize)

#submit futures to executor
futures = {}
for run in range(0, numOfRuns):
    for bdg in BDGS:
        futures[executor.submit(runTest, URLS[env] % bdg, bdg, testerStack, components, flagCount)] = bdg

totalRuns = len(futures)
print str(totalRuns) + " futures loaded."

#print indications as futures complete
runCount = 0
for future in concurrent.futures.as_completed(futures):
    bdg = futures[future]
    try:
        result = future.result()
        if result != []:
            csvWriter.writerow(future.result())
            csvOutFile.flush()
        else:
            print "%s skipped!" % bdg
    except Exception as exc:
        print('%s generated an exception: %s' % (bdg, exc))
        printTraceback()


    runCount += 1
    print str(runCount) + "/" + str(totalRuns) + " - " + bdg + " completed."

for tester in testerStack:
    tester.nuke()


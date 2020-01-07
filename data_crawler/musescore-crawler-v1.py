from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.wait import WebDriverWait
import time
import random
import os
import subprocess
import sys, getopt

def crawl(minPage,maxPage,outputFormat):
    # set selenium proxy
    prox = Proxy()
    prox.proxy_type = ProxyType.MANUAL
    prox.http_proxy = "http://localhost:8118"
    prox.ssl_proxy = "http://localhost:8118"
    capabilities = webdriver.DesiredCapabilities.CHROME
    prox.add_to_capabilities(capabilities)

    #initialize driver 
    driver = webdriver.Firefox()
    driver.get("http://www.musescore.com")
    button = driver.find_element_by_class_name("login")
    button.click()

    #click on cookies modal so it doesn't obscure buttons
    cookies_modal = WebDriverWait(driver, 10).until(
                        lambda x: x.find_element_by_xpath("//button[@class='agree-button']"))
    driver.execute_script("arguments[0].click();",cookies_modal)
    time.sleep(random.randint(5, 10))

    #crawl
    for page in range(minPage,maxPage+1):
        url = "https://musescore.com/hub/piano?page=" + str(page)
        print("crawling page: "+ str(page))
        #clear if no of pages is too big
        if page % 5 == 0:
            subprocess.call("killall -HUP tor", shell = True)
            time.sleep(1)
        for index in range(1,21):
            #select score from grid
            driver.get(url) # go back to grid of scores
            score_list = driver.find_elements_by_xpath("//h2[@class='score-info__title']")
            try:
                score_list[index].click()
                #download
                driver.execute_script(open("musescore-downloader.js").read())
                #try twice, if still error move on

                download_button = WebDriverWait(driver, 10).until(
                        lambda x: x.find_elements_by_xpath("//button[@class='_3L7Ul _3qfU_ _38TLP _3A7i9 _2XPrY _13O-4 _15kzJ']"))
               
                #XML
                if outputFormat == 'XML':
                    download_button[2].click()
                #MIDI
                elif outputFormat == 'MIDI':
                    download_button[3].click()
                else:
                    print("Incorrect usage! please type:"
                        + "musescore-crawler.py -f <format> -s <minPage> -e <maxPage>")
                    sys.exit(2)

                time.sleep(random.randint(10,30))
                time.sleep(5)
            except:
                print("Failed opening score, move on to next")

def read_sys_args(argv):
    '''Read commands from command line'''
    mode = None
    outputFormat = None
    minPage = 0
    maxPage = 0

    try:
        opts, args = getopt.getopt(argv,"hf:s:e:")
    except getopt.GetoptError:
        print("Incorrect usage! please type:"
        + "musescore-crawler.py -f <format> -s <minPage> -e <maxPage>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("Help: This is a MuseScore crawler. \n"
            + "You can crawl the most recent piano scores .\n"
            + "Pass the format (MIDI or XML) as the -f argument.\n"
            + "Pass the number of page to begin crawling as the -s argument.\n"
            + "Pass the number of pages to end crawling as the -e argument.\n"
            + "Usage: musescore-crawler.py -f <format> -s <minPage> -e <maxPage>\n")
            sys.exit()
        elif opt in ("-f", "--format"):
            outputFormat = arg
        elif opt in ("-s", "--minPage"):
            minPage = int(arg)
        elif opt in ("-e", "--maxPage"):
            maxPage = int(arg)
        else:
                print("Incorrect usage! please type:"
                + "musescore-crawler.py -f <format> -s <minPage> -e <maxPage>")
                sys.exit(2)

    crawl(minPage,maxPage,outputFormat)
    print("Done")

if __name__ == '__main__':

    print("Hi, welcome to MuseScore Crawler")
    read_sys_args(sys.argv[1:])
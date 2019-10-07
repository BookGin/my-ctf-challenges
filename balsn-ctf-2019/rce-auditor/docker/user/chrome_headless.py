#!/usr/bin/env python3
import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

loading_page_time_sec = 5
browsing_page_time_sec = 5

def browse(url):
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox') # https://stackoverflow.com/a/45846909
    options.add_argument('--disable-dev-shm-usage') # https://stackoverflow.com/a/50642913
    chrome = Chrome(options=options)
    # https://stackoverflow.com/a/47695227
    chrome.set_page_load_timeout(loading_page_time_sec)
    chrome.set_script_timeout(loading_page_time_sec)
    try:
        chrome.get(url)
        time.sleep(browsing_page_time_sec)
    except (TimeoutException, WebDriverException):
        pass
    finally:
        chrome.quit()

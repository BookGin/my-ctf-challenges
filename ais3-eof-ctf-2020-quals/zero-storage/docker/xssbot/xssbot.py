#!/usr/bin/env python3
import time, os

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

loading_page_time_sec = int(os.environ['LOAD_TIME_SEC'])

'''
[
  {
      'url': 'http://example.com',
      'timeout': 5,
      'cookies': {
          'key': 'value'
      }
  }
]
'''
def browse_all(urls):
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') # https://stackoverflow.com/a/50642913
    chrome = Chrome(options=options)
    # https://stackoverflow.com/a/47695227
    chrome.set_page_load_timeout(loading_page_time_sec)
    chrome.set_script_timeout(loading_page_time_sec)
    for u in urls:
        try:
            chrome.get(u['url'])
            for name, value in u.get('cookies', {}).items():
                chrome.add_cookie(dict(name=name, value=value))
            time.sleep(u.get('timeout', 5))
        except (TimeoutException, WebDriverException):
            pass
    chrome.quit()

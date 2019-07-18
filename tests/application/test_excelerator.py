import pytest
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import os

def test_exelerator_200_response():
    '''Test
    '''
    EXELERATOR_URL = os.getenv("EXCELERATOR_URL")
    response = requests.get(EXELERATOR_URL)
    assert(response.status_code == requests.codes.ok)

def test_exelerator_valid_page_contents():
    '''Test
    '''
    chrome_options = webdriver.chrome.options.Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(10)
    EXELERATOR_URL = os.getenv("EXCELERATOR_URL")
    driver.get(EXELERATOR_URL)
    assert(driver.title == 'Excelerator')
    #assert(len(found_elements) > 0)
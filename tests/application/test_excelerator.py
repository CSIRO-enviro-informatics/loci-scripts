import pytest
import requests
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
    assert(True)
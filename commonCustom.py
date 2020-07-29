from requests import get
from bs4 import BeautifulSoup, SoupStrainer
from lbcapi3 import api 
import urllib.request, json


def getJSON_API(base_url, endpoint):
    urlReader=urllib.request.urlopen(base_url + endpoint)
    API_Data=json.loads(urlReader.read())
    return API_Data

def openParsePage(url, elemStrainer,jsonStrainer):
    partialSoup= SoupStrainer(elemStrainer, jsonStrainer)
    rawPage=get(url)
    soup=BeautifulSoup(rawPage.content,parse_only=partialSoup, features='html.parser')
    return soup

import requests
from bs4 import BeautifulSoup
from random import shuffle

with open('names.txt','r', encoding='utf-8')as f:
    lines = f.readlines()
any = []
for line in lines:
    if line.strip().capitalize() == line.strip() and len(line.strip())<20:
        any.append(line.strip())
shuffle(any)
for x in any:
    print(x.capitalize())
import requests
from bs4 import BeautifulSoup
import json

all_cookies = dict()
headers = dict()
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
restaurants = [["" for x in range(4)] for y in range(20)] 

def get_cookies():
    global all_cookies

    f = open("cookies.json","r")
    cookiedata = f.read()
    f.close()

    cookiedata = json.loads(cookiedata)

    for i in cookiedata:
        name = i["name"]
        value = i["value"]
        all_cookies[name] = value

def connect_zomato():
    r = requests.get("https://zomato.com", cookies=all_cookies, headers=headers)
    if("Log out" in r.text):
        print("Logged in!")
    else:
        print("Invalid cookies")

def scrape_restaurants(dish, pg_no):
    r = requests.get("https://www.zomato.com/id/jakarta/kemang-restoran?q=%s&page=%d"%(dish,pg_no), headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    divs = soup.find_all("div",{'class':'search-snippet-card'})
    i = 0
    for div in divs:
        res_name = div.findChildren("a",{'class':'result-title'})
        res_rating = div.findChildren("span",{'class':'rating-value'})
        res_address = div.findChildren("div",{'class':'search-result-address'})
        res_price = div.find_all("div",{'class':'search-page-text'})
        for a in res_name:
            name = a.text
            restaurants[i][0] = name
        for a in res_rating:
            rating = a.text
            restaurants[i][1] = str(rating)
        for a in res_address:
            address = a.text
            restaurants[i][2] = address
        for price in res_price:
            res_price_children = price.findChildren("div",{'class':'res-cost'})
            for a in res_price_children:
                the_real_price = a.findChildren("span",{'class':'col-s-11'})
                for b in the_real_price:
                    price = b.text
                    restaurants[i][3] = str(price)
        i = i+1
    return restaurants

for i in range(1,3):
    print(scrape_restaurants("sushi",i))
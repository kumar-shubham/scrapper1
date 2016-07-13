import requests
import re
from bs4 import BeautifulSoup as bs
import json, operator,sys,time

url = "http://www.aliexpress.com/"

categories = ["Consumer Electronics", "Jewelry", "Watches", "Health & Beauty"]

r = requests.get(url)

soup = bs(r.content, "html.parser")
product = {}
links = []

def getProductDetail(plink,category):
    s = requests.get(plink)
    page = bs(s.content, "html.parser")
    #print "inside product details"
    prod = {}
    #print category
    product_name = page.find("h1",{"class":"product-name"})
    if product_name is not None:
        product_name = product_name.text
    rating = page.find("span", {"class":"percent-num"})
    if rating is not None:
        rating = rating.text
    image = page.find("div",{"class":"ui-image-viewer-thumb-wrap"})
    if image is not None:
        image = image.img['src']

    price = page.find("span",{"itemprop":"lowPrice"})
    if price is None:
        price = page.find("span", {"id":"j-sku-discount-price"})
    if price is None:
        price = page.find("span",{"id":"j-sku-price"})
    if price is not None:
        price  = price.text

    desc = page.find("#j-product-description > div.ui-box-body > div > p:nth-child(2)")
    if desc is not None:
        desc = desc[0].text
    if desc is None or len(desc) < 30:
        desc = page.find("#j-product-description > div.ui-box-body > div > p:nth-child(3)")
    if desc is not None:
        desc = desc[0].text

    cat = page.find("a", text=re.compile('All Categories'))
    if cat is not None:
        cat = cat.find_next_sibling("a").find_next_sibling("a")
    if cat is not None:
        cat = cat.text

    feedback_block = page.find("div",{"id":"feedback"})
    feedback_url = None
    if feedback_block is not None:
        feedback_url = feedback_block.iframe["thesrc"]
    feedbacks = []
    if feedback_url is not None and "http:" not in feedback_url:
        feedback_url = "http:" + feedback_url
        f = requests.get(feedback_url)
        fb_page = bs(f.content, "html.parser")
        feedbacks = fb_page.find_all("div", class_="feedback-item clearfix")
    feedback = []
    #print feedbacks
    for fb in feedbacks:
        feed = {}
        user_name = fb.find("span", {"class":"user-name"})
        if user_name is not None:
            user_name = user_name.text
        comment = fb.find("dt", {"class":"buyer-feedback"})
        if comment is not None:
            comment = comment.find_next("span").text
        time = fb.find("dd", {"class":"r-time"})
        if time is not None:
            time = time.text
        feed['user_name'] = user_name
        feed['comment'] = comment
        feed['time'] = time
        feedback.append(feed)
    prod['product_name'] = product_name
    prod['category'] = cat
    prod['image'] = image
    prod['price'] = price
    prod['rating'] = rating
    prod['description'] = desc
    prod['link'] = plink
    prod['reviews'] = feedback

    if category not in product:
        product[category] = [prod]
    else:
        product[category].append(prod)
    
    
    #print "  description   :: " + str(desc)
    #print "  prodduct name :: " + str(product_name)
    #print "  category      :: " + str(cat)
    #print "  rating        :: " + str(rating)
    #print "  price         :: " + str(price)
    #print "  image         :: " + str(image)
   

def getCategoryLink():   
    for cat in categories:
        link = soup.find("a",text=re.compile(cat)).get("href")
        if link is not None:
            links.append(link.replace("//",""))


def getProductLink():
    count = -1
    timer = 0
    for link in links:
        count += 1
        sub_links1 = []
        product_links = []
        if "http://" not in link:
            link = "http://" + link
        r = requests.get(link)
        soup = bs(r.content, "html.parser")
        #print "Main Link :: " + link

        sub_list = []
        if "consumer-electronics" in link:
            sub_list = soup.find_all("h2", {"class":"bc-big-row-title bc-nowrap-ellipsis"},limit=2)
        elif "jewelry" in link or "watches" in link:
            sub_list = soup.find_all("div", {"class":"bc-row-wrap"},limit=2)
        elif "health-beauty" in link:
            sub_list = soup.find_all("p", {"class":"bc-main-name bc-nowrap-ellipsis"},limit=2)

        for item in sub_list:
            temp =  item.find("a").get("href")
            if temp is not None:
                if "http:" not in temp:
                    temp = "http:" + temp
                sub_links1.append(temp)

        for sub_link in sub_links1:
            #print " " + sub_link
            r = requests.get(sub_link)
            soup = bs(r.content, "html.parser")
            products = soup.find_all("a",class_="product", limit=5)
            for product1 in products:
                prod_url = product1.get("href")
                if "http:" not in prod_url:
                    prod = "http:" + prod_url
                    product_links.append(prod)
            
        for prod_link in product_links:
            timer += 2.5
            if timer % 1 == 0:
                update_progress_bar(timer)
            #print "  aa " + prod_link
            getProductDetail(prod_link,categories[count])

def update_progress_bar(num):
    percent = float(num) / 100
    bar_length = 50
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rPercent Scraped: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()




if __name__ == "__main__":
    
    update_progress_bar(0)
    getCategoryLink()
    getProductLink()
    for dicts in product:
        product[dicts] = sorted(product[dicts], key=operator.itemgetter('price'), reverse=True)    
    result = json.dumps(product)
    with open("product.json", "w+") as json_file:
        json_file.write(result)

    print ' Done!'
    print result





import requests
import re
from bs4 import BeautifulSoup as bs
import json, operator,sys,time
from fake_useragent import UserAgent

ua = UserAgent()
url = "http://www.aliexpress.com/"
cookies = {'acs_usuc_t':'acs_rt=292fb5775fcb4aa78fdbcaf9f3663308',
           'ali_apache_track':'"mt=1|mid=in1121057498ukto"',
           'ali_apache_tracktmp':'"W_signed=Y"',
           'intl_common_forever':'lPbvEhUTvOEkFWzdcBKSEA51TYTQFw9IXWRF0LHiA15rsUcuuKHhTg==',
           'intl_locale':'en_US',
           'xman_f':'j1mGELwPTOO/da1J1D8OlkWMcfrIhMFwI4HjaA4cMJcp9rl00nkI27yCKOtf6J+8h2xuemtKrIiQTUJQvvM2daY85Emlp0Ia6v6EH7eJqdGVpc0gn9gPDGHz49KrlwPKJL7LrOL/DqQeD2G2q8yFdzkXWijp0vuX5CWNdOa2Vq8bJ5EkJ12V15QW+0bXdWmdfQmK5TWWGZnzOTwip++l/n1yuCXTRwQ2sbuDYHp1g0IBezv2XFQP85cQtTPDYp3D6FgAkPwIrfAOIkmDWLUCVp1RlZlcGfp86aEtlz5j8R1WLaDUQKPEP2VyqyVVB2gsDe42b82IgJGWYwbNPmdVlI7pK1wS4taV6ce0lw1TQStteXkDniU3yr8IE6akYbu9mfqLjIR4gdE=',
           'xman_t':'Z8INVgnKTjwqQzOUQ+xvaaQ8ViH4nRCG0nJ7H85RjXZArVcW9bFqYyugf5AIkYq8gDLqOfs+8b1OMeFtx40wgoN6SA0Q2+KVr5LFl8W/f3dVx/5/i6bbNJXbkmkq+0j4me9Sj/BcuRJCinJzykvcOjRKEg3sDj+jKXYdvbSJH2Yx1uDTpBFd2Wjd/gcimYzn/kPyWkfSuCfubxH/F39QEd97FcUZrHeu5OT7Bj4iZlc3xWpIO5FYVUF4+0GxIFBNDU7awW04dncKgxJcAsDb40E9EFe1QPy9U6qucEUAtxnmB4M4etzhqL+fHfuzi1uW60LWstbCjyduJ+B8KP91MlIth5stB0ioVkDDejkV9su5CILWAbj2g4MaeLJAYIelzxvXNdI8Pmh5ayLyfR3UD5T2Z/XyUEmc270/oV/+XCTI9VwQa3Qgxo1pboy3u8CrIXdNVVVPKsJhdQTeRf6yduJDKAex2hp1ctSmP59rEq/Jh5KMIaOhhQ4ssQN9UabPWiqqbu6I+CLJR2DlajzJcnNJ4X114DGyUqDetJM5E7a/Uu51Uegy66h9dWrTfmocfXpvK/RTcqj6iE3OD/ZbTYmlyGV1d7tg8x+dSO1brbr1qudouq4+Ls3BijObeZW7+tSRJt1JJ1DHMq3EO99Qxj0aOio7x2C9',
           'xman_us_f':'x_l=0&x_locale=en_US&no_popup_today=n&x_user=IN|Kumar|Shubham|ifm|740451827&last_popup_time=1468427270358',
           'xman_us_t':'x_lid=in1121057498ukto&sign=y&x_user=JRkzRdM4U6/kMi94GwEyDWuV9ks1LmpdtqARmUrkf3U=&ctoken=5pfp56002mg5&need_popup=y'
           }

categories = ["Consumer Electronics", "Jewelry", "Watches", "Health & Beauty"]
header = {'User-Agent': ua.random}
r = requests.get(url, headers=header,cookies=cookies)

soup = bs(r.content, "html.parser")
product = {}
links = []
prod_limit = 100
sub_cat_limit = 2

def getProductDetail(plink,category):
    header = {'User-Agent': ua.random}
    try:
        s = requests.get(plink,headers=header,cookies=cookies)
    except:
	print "failure url ::::::: " + plink
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
    product_link_dict = {}
    sub_link_dict = {}
    for link in links:
        sub_links1 = []
        count += 1
        if "http://" not in link:
            link = "http://" + link
        header = {'User-Agent': ua.random}
        try:
            r = requests.get(link,headers=header)
        except:
	    print "failure url link ::::::: " + link
        soup = bs(r.content, "html.parser")
        #print "Main Link :: " + link

        sub_list = []
        if "consumer-electronics" in link:
            sub_list = soup.find_all("h2", {"class":"bc-big-row-title bc-nowrap-ellipsis"},limit=sub_cat_limit)
        elif "jewelry" in link or "watches" in link:
            sub_list = soup.find_all("div", {"class":"bc-row-wrap"},limit=sub_cat_limit)
        elif "health-beauty" in link:
            sub_list = soup.find_all("p", {"class":"bc-main-name bc-nowrap-ellipsis"},limit=sub_cat_limit)

        for item in sub_list:
            temp =  item.find("a").get("href")
            if temp is not None:
                if "http:" not in temp:
                    temp = "http:" + temp
                sub_links1.append(temp)
        sub_link_dict[categories[count]] = sub_links1
        product_links = []
        for sub_link in sub_link_dict[categories[count]]:
           #print " " + sub_link
            try:
                r = requests.get(sub_link,headers=header)
            except:
	        print "failure url sub_link ::::::: " + sub_link
            soup = bs(r.content, "html.parser")
            products = soup.find_all("a",class_="product", limit=prod_limit)
            for product1 in products:
                prod_url = product1.get("href")
                if "http:" not in prod_url:
                    prod = "http:" + prod_url
                    product_links.append(prod)
            product_link_dict[categories[count]] = product_links

    size = 0
    for key in product_link_dict:
        size +=  len(product_link_dict[key])
                
    update_value = size*1.0/100
    divider = int(update_value+1)
    timer = 0
    #print str(size) + "::"
    for key in product_link_dict:
        for prod_link in product_link_dict[key]:
            if timer % int(divider) == 0:
                #print int(timer/update_value)
                update_progress_bar(int(timer/update_value))
            #print "  aa " + prod_link
            getProductDetail(prod_link,key)
            timer += 1
    update_progress_bar(100)

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
    print "hello"
    getProductLink()
    for dicts in product:
        product[dicts] = sorted(product[dicts], key=operator.itemgetter('price'), reverse=True)    
    result = json.dumps(product)
    with open("product.json", "w+") as json_file:
        json_file.write(result)

    print ' Done!'
    print result





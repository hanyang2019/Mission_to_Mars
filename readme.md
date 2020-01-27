![mars](https://natgeo.imgix.net/shows/thumbnails/MarsS2_KeyArt-Horizontal_1920x1080_CLEAN.jpg?auto=compress,format&w=1920&h=960&fit=crop)
# __Mission to Mars__
## __Goal__
To build a web application that scrapes various websites for data related to the Mission to Mars and displays the information in a single HTML page.

---
## __Data Source__
* [NASA Mars News](https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest)
* [JPL Mars Image](https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars)
* [Mars Weather](https://twitter.com/marswxreport?lang=en)
* [Mars Facts](https://space-facts.com/mars/)
* [USGS Astrogeology](https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars)
---
## __Tools__
* Python
* MongoDB
* HTML/CSS
----------
## __App Set-up__
Import dependencies (Make sure to start MongoDB before running the app).
```python
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars
```
Create an instance of Flask class and connect to MongoDB.
```python
app=Flask(__name__)
mongo=PyMongo(app, uri="mongodb://localhost:27017/mars_db")
```
Get data from MongoDB and render it to index.html.
```python
@app.route('/')
def index():
    content=mongo.db.results.find_one()
    return render_template('index.html',dict=content)
```
Start web scraping and store returned results into MongoDB.
```python
@app.route('/scrape')
def scraper():
    data=scrape_mars.scrape()
    mongo.db.results.update_one({},{"$set": data},upsert=True)
    return redirect('/',code=302)
```
Run the app.
```python
if __name__=='__main__':
    app.run()
```
---
## __Web Scraping__
Import dependencies
```python
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from splinter import Browser
import time
```
Define a function to activate chrome driver.
```python
def init__browser():

    executable_path={'executable_path':'/usr/local/bin/chromedriver'}
    return Browser('chrome',**executable_path,headless=False)
```
Define a function to trigger web scraping and create an empty dictionary to store all returned reults.
Scrape the [NASA Mars News Site](https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest) and collect the latest News Title and Paragraph Text. 
```python
def scrape():

    scrapping_results={}
    browser=init__browser()
    nasa_url="https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(nasa_url)
    html=browser.html
    soup=bs(html,'html.parser')
    latest_news_title=soup.find('div',{"class":"content_title"}).a.text.strip()
    scrapping_results['latest_news_title']=latest_news_title
    latest_news_p=soup.find('div',{"class":"rollover_description_inner"}).text
    browser.quit()
    scrapping_results['latest_news_p']=latest_news_p
```
Visit [JPL Featured Space Image](https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars) to find the image url for the current Featured Mars Image.
```python
    browser=init__browser()
    jpl_url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(jpl_url)
    browser.click_link_by_partial_text('FULL IMAGE') 
    time.sleep(5) 
    browser.click_link_by_partial_text('more info') 
    html=browser.html
    soup=bs(html,'html.parser')
    result=soup.find('figure',{'class':'lede'}).a['href']
    jpl_base_url='https://www.jpl.nasa.gov/'
    jpl_featured_image_url=jpl_base_url+result
    scrapping_results['jpl_img']=jpl_featured_image_url
    browser.quit()
```
Visit the [Mars Weather twitter account](https://twitter.com/marswxreport?lang=en) to scrape the latest Mars weather tweet from the page.
```python
    browser=init__browser()
    twitter_url='https://twitter.com/MarsWxReport'
    browser.visit(twitter_url)
    html=browser.html
    soup=bs(html,'html.parser')
    results=soup.find_all('p',{'class':'TweetTextSize'})
    try:
        for tweet in results:
            unwanted=tweet.find('a')
            unwanted.extract()
    except AttributeError:
            print('ok')
    tweet_list=[tweet.text.strip() for tweet in results]
    for tweet in tweet_list:
        if ('InSight sol' in tweet):
            mars_weather=tweet.lstrip('InSight ')
            break
    scrapping_results['latest_tweet']=mars_weather
    browser.quit()
```
Visit the [Mars Facts webpage](https://space-facts.com/mars/)  to scrape the table containing facts about the planet including Diameter, Mass, etc.
```python
    browser=init__browser()
    mars_facts_url='https://space-facts.com/mars/'
    browser.visit(mars_facts_url)
    html=browser.html
    soup=bs(html,'html.parser')
    first_column=soup.find_all('td',{'class':'column-1'})
    first_column_content=[i.text for i in first_column]
    second_column=soup.find_all('td',{'class':'column-2'})
    second_column_content=[i.text for i in second_column]
    table_df=pd.DataFrame({'Description':first_column_content,'Value':second_column_content})
    mars_facts_html_table=table_df.to_html(index=False,justify='center')
    scrapping_results['table']=mars_facts_html_table
    browser.quit()
```
Visit the [USGS Astrogeology site](https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars) to obtain high resolution images for each of Mar's hemispheres.
```python
    browser=init__browser()
    url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    html=browser.html
    soup=bs(html,'html.parser')
    titles=soup.find_all('h3') 
    title_list=[title.text for title in titles]
    usgs_base_url='https://astrogeology.usgs.gov'
    next_page_urls=soup.find_all('div',{'class':'description'}) 
    next_page_full_url_list=[usgs_base_url+url.a['href'] for url in next_page_urls]
    original_image_url_list=[]
    for url in next_page_full_url_list:
        browser.visit(url)
        html=browser.html
        soup=bs(html,'html.parser')
        url=soup.find_all('li') 
        original_image_url_list.append(url[0].a['href'])
    browser.quit()   
    hemisphere_image_urls=[dict(title=title_list[i].replace(' Enhanced',''), img_url=original_image_url_list[i]) for i in range(4)]
    scrapping_results['hemisphere']=hemisphere_image_urls            

    return scrapping_results
```
---
## __Preview__
![screenshot](https://github.com/hanyang2019/Mission_to_Mars/blob/master/screen_shot.png?raw=true)
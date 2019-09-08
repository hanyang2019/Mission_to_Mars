import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from splinter import Browser
import time

def init__browser():

    executable_path={'executable_path':'/usr/local/bin/chromedriver'}
    return Browser('chrome',**executable_path,headless=False)

def scrape():

    scrapping_results={}
# NASA Mars News
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

# JPL Mars Featured Image
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

# Mars Weather
    browser=init__browser()
    twitter_url='https://twitter.com/MarsWxReport'
    browser.visit(twitter_url)
    html=browser.html
    soup=bs(html,'html.parser')
    results=soup.find_all('p',{'class':'TweetTextSize'})
    tweet_list=[tweet.text.strip() for tweet in results] 
    for tweet in tweet_list:
        if ('InSight sol' in tweet):
            mars_weather=tweet.lstrip('InSight ')
            break
    scrapping_results['latest_tweet']=mars_weather
    browser.quit()

# Mars Facts
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

# Mars Hemispheres
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






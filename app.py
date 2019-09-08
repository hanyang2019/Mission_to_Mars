from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app=Flask(__name__)
mongo=PyMongo(app, uri="mongodb://localhost:27017/mars_db")

@app.route('/')
def index():
    content=mongo.db.results.find_one()
    return render_template('index.html',dict=content)

@app.route('/scrape')
def scraper():
    data=scrape_mars.scrape()
    mongo.db.results.update_one({},{"$set": data},upsert=True)
    return redirect('/',code=302)

if __name__=='__main__':
    app.run()
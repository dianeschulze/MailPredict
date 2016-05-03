# Based on https://github.com/zachwill/flask_heroku

import os
from flask import Flask, render_template, request, redirect, url_for
from sklearn.externals import joblib
import csv
import simplejson as json

app = Flask(__name__)

# IFTTT variables; configure for your own account
FROM_IFTTT_SECRET = os.getenv('IFTTT_SECRET')
TO_IFTTT_KEY = os.getenv('TO_IFTTT_KEY')
IFTTT_BASE_URL = os.getenv('IFTTT_BASE_URL')
my_email_address = 'diane_schulze@brown.edu'
# Whitelist of people to send auto-responses to
whitelist = set(['diane_schulze@brown.edu', 'dschulze2@gmail.com', 'jeff_huang@brown.edu', 'nediyana_daskalova@brown.edu','austin.whitt@gmail.com'])

# load the regression model 
model = joblib.load('model/regression_model.pkl') 

# Populate the sender lookup table, which maps from email address to my average time to respond to that person
sender_lookup = {}
with open('data/sender_table.csv', 'rb') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        sender_lookup[row[0]] = float(row[1])

@app.route("/")
def hello():
    return 'Hi I am an email server'

@app.route("/email", methods = ['POST'])
def gotMail():
    secret = request.form['secret']
    sender = request.form['sender']
    date = request.form['date']
    subject = request.form['subject']
 
    if secret == FROM_IFTTT_SECRET:
        # obvious emails to not reply to
        #if not('morning_mail' in sender or 'no-reply' in sender or 'no-reply' in sender or 'unsubscribe' in body):
        
        #or just use a small whitelist
        #if sender in sender_lookup and sender in whitelist:# Only sending an auto-reply if I've replied to this person before
       
        # or since I'm sending auto-replies to myself right now, I can just send them for any senders I have data on
        if sender in sender_lookup:# Only sending an auto-reply if I've replied to this person before

            # Get the features for this email
            #regression features: [average response time to this sender, whether the sender has a brown.edu address]          
            avg_resp_time = sender_lookup[sender]
            brown_sender = 0
            if 'brown.edu' in sender:
                brown_address = 1

            seconds = model.predict([[avg_resp_time, brown_sender]])[0][0]
            hours = str(round(seconds/float(60*60),2))

            # send the response email 
            # value1 = address to send the auto-response to
            # value2 = subject line from the email they sent me
            # value3 = predicted response time in hours
            reply_data = {"value1": my_email_address, "value2":subject, "value3":hours}
            json_str = json.dumps(reply_data)

            reply_url = IFTTT_BASE_URL+TO_IFTTT_KEY
            headers = {'Content-Type': 'application/json'}
            req = requests.post(reply_url, data=json.dumps(reply_data), headers=headers)
            #req = requests.post(reply_url, data=json_str)

        return 200    

    else:
        print "no from ifttt secret"
        return 400


if __name__ == '__main__':
    app.run(port = os.getenv('PORT', 8000))

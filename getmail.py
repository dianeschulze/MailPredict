import imaplib, email, getpass
from email.utils import getaddresses
from collections import defaultdict
from datetime import datetime
from dateutil import parser
import numpy
import csv
# This script is based on this tutorial from Nathan Yau: https://flowingdata.com/2014/05/07/downloading-your-email-metadata/


imap_server = 'imap.gmail.com'
imap_user = 'diane_schulze@brown.edu'
imap_password = getpass.getpass()

conn = imaplib.IMAP4_SSL(imap_server)
(retcode, capabilities) = conn.login(imap_user, imap_password)

# First get all of my sent mail and store it in a hashmap by in-reply-to ID
conn.select("[Gmail]/Sent Mail", readonly = True)
result, data = conn.uid('search', None, '(SINCE "01-Sep-2015" BEFORE "30-May-2016")')
sent_uids = data[0].split()
result, data = conn.uid('fetch', ','.join(sent_uids), '(BODY[HEADER.FIELDS (MESSAGE-ID FROM TO CC DATE IN-REPLY-TO)])')

#lookup table from the id of an incoming message to a tuple with info about the message(s) I sent in response
# tuple structure: (response message ID, response timestamp, [receivers])
sentDict = defaultdict(lambda:[])
for i in range(0, len(data)):
     
    # If the current item is _not_ an email header
    if len(data[i]) != 2:
        continue   
    # Parse the email header
    msg = email.message_from_string(data[i][1])
    mids = msg.get_all('message-id', None)
    mdates = msg.get_all('date', None)
    receivers = msg.get_all('to', [])
    reply_to = msg.get_all('in-reply-to', [])

    if len(reply_to) > 0:
        for m_id in reply_to:
            sentDict[m_id].append((mids[0],mdates[0], receivers))

# *********** Now get all incoming mail *************
conn.select("[Gmail]/All Mail", readonly = True)
result, data = conn.uid('search', None, '(SINCE "01-Sep-2015" BEFORE "30-May-2016")')
uids = data[0].split()

result, data = conn.uid('fetch', ','.join(uids), '(BODY[HEADER.FIELDS (MESSAGE-ID FROM TO CC DATE)])')

senderTimes = defaultdict(lambda:[]) # dictionary from sender to reply time, used to calculate average and median reply times
rows = [] # store data that I'll write to a file in the end

# *************** Parse incoming email data, extract features, store them in a list ******************
for i in range(0, len(data)):
     
    # If the current item is _not_ an email header
    if len(data[i]) != 2:
        continue
     
    # Okay, it's an email header. Parse it.
    msg = email.message_from_string(data[i][1])
    mids = msg.get_all('message-id', None)
    mdates = msg.get_all('date', None)
    senders = msg.get_all('from', [])
    receivers = msg.get_all('to', [])
    ccs = msg.get_all('cc', [])

    if 'no-reply' in senders[0].lower() or 'noreply' in senders[0].lower(): # not even relevant at all, for the classifier or regression
        continue

    # parse the received date  
    try:
        senttime = parser.parse(mdates[0]) #when did I get the email
    except(ValueError):
        senttime = parser.parse(mdates[0].split('(')[0]) # if it can't parse the date, it's probably because it ends in something like (GTM+00:00). So you can jsut remove that. 
    
    # there's only 2 timezone unaware dates and they're a huge pain so I just skip them
    if senttime.tzinfo is None or senttime.tzinfo.utcoffset(senttime) is None: 
        continue


    for name, addr in getaddresses(senders):
        sender = addr # there's actually only one sender per email


    # ********* get some features from the time when I received the email (senttime) *****************
    # categories: weekday, week evening, week night (meaning I'm asleeep), weekend day, weekend evening (including friday and sunday), weekend night
    dayofweek = senttime.weekday()
    hour = senttime.hour

    # turning categorical data with k categories into k-1 binary features
    if dayofweek == 6 or dayofweek == 7: # sat and sun
        if 0 <= hour < 11:
            (is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve) = 0,0,0,0,0
        elif  11 <= hour <= 19:
            (is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve) = 0,0,0,1,0
        elif 19 < hour < 24:
            (is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve) = 0,0,0,0,1
    elif dayofweek == 5: # friday is a special case
        if 0 <= hour < 9:
            (is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve) = 0,0,1,0,0
        elif  9 <= hour <= 18:
            (is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve) = 1,0,0,0,0
        elif 18 < hour < 24:
            (is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve) = 0,0,0,0,1
    else: # mon-thurs
        if 0 <= hour < 9:
            (is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve) = 0,0,1,0,0
        elif  9 <= hour <= 18:
            (is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve) = 1,0,0,0,0
        elif 18 < hour < 24:
            (is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve) = 0,1,0,0,0
        # else is a weekend night, but not including that as a feature bc then the features are linearly dependent
    
    # *****other features **********

    # how many people received the email?
    num_recipients = len(receivers)+len(ccs)

    # did it come from a brown email address?
    brown_sender = 0
    if '@brown.edu' in sender.lower():
        brown_sender = 1


    # get my reply data from the dictionary
    reply = sentDict[mids[0]] # mids never has more than 1 element in my data

    if len(reply) > 0: #interested in the first reply
        replied = '1'

        # date parsing
        replytime = parser.parse(reply[0][1]) #when did I reply
        
        # get the time it took to reply in seconds
        time_to_reply = (replytime-senttime).total_seconds()

        # add my response time to a dictionary w/ sender as the key 
        senderTimes[sender].append(time_to_reply)

    # recording that there was no reply so I can build a binary reply classifier if I have time
    else:
        replied = '0'
        replytime = ''
        time_to_reply = ''

    row = []
    row.append('' if not mids else mids[0])
    row.append('' if not mdates else mdates[0])
    row.append(sender)
    row.append(replied)
    row.append(str(replytime))
    row.append(str(time_to_reply))
    row.append(str(is_weekday))
    row.append(str(is_weekeve))
    row.append(str(is_weeknight))
    row.append(str(is_weekendday))
    row.append(str(is_weekendeve))
    row.append(str(num_recipients))
    row.append(str(brown_sender))
    
    rows.append(row)


# *********** Go through sender dictionary, calculate the average and median response time for each sender. Output the sender-averge response time dict to a file********
with open('data/sender_table.csv','w') as out:
    owriter = csv.writer(out)
    owriter.writerow(['sender','avg_resp_time'])
    for sender in senderTimes:
        times = senderTimes[sender]
        avg = numpy.average(times)
        med = numpy.median(times)
        senderTimes[sender] = (avg,med)
        owriter.writerow([sender, str(avg)])

# *********** Write output to a CSV file ******************
with open('data/recent-email-output2.csv', 'w') as out:
    writer = csv.writer(out)
    # header
    writer.writerow(['message_id', 'received_date', 'sender', 'replied', 'reply_date', 'time_to_reply', 'is_weekday', 'is_weekeve','is_weeknight', 'is_weekendday', 'is_weekendeve', 'num_recipients', 'brown_sender','sender_avg_resp_time', 'sender_med_resp_time'])

    for row in rows:
        sender = row[2]
        if sender in senderTimes:
            (avg,med) = senderTimes[sender]
            row.append(str(avg))
            row.append(str(med))
        else: 
            row.append('')
            row.append('')
        writer.writerow(row)



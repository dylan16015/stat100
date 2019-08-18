#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 21:08:10 2019

@author: dylan
"""

import tweepy
import pandas as pd
import time

f=open("twitter_dev_credentials.txt", "r")
creds = f.readlines()
consumer_key = creds[0].strip()
consumer_secret = creds[1].strip()
f.close()

#%%

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth_handler=auth, parser=tweepy.parsers.JSONParser())

mps =   [
        'billshortenmp',
        'PaulFletcherMP',
        'NicolleFlint',
        'andrewjgiles',
        'markdreyfusQCMP',
        'karenandrewsmp',
        'ShayneNeumannMP',
        'MadeleineMHKing',
        'BertVanManen',
        'NickChampionMP',
        ]

df = pd.DataFrame(columns = ['politician', 'tweet_dt'])

#%%
sitting_week_start = pd.to_datetime('2019-07-22')
sitting_week_end = pd.to_datetime('2019-07-26')
electorate_week_start = pd.to_datetime('2019-07-15')
electorate_week_end = pd.to_datetime('2019-07-19')

#%%
start_date = min([sitting_week_start, sitting_week_end, electorate_week_start, electorate_week_end])
finish_date = max([sitting_week_start, sitting_week_end, electorate_week_start, electorate_week_end])

for mp in mps:
    current_date = finish_date
    current_id = None
    tweet_dt = []
    while current_date > start_date:
        user_tweets = api.user_timeline(mp, max_id = current_id)
        current_date = user_tweets[-1]['created_at']
        current_date = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(current_date,'%a %b %d %H:%M:%S +0000 %Y'))
        current_date = pd.to_datetime(current_date)
        current_id = user_tweets[-1]['id']
        for tweet in user_tweets:
            td = tweet['created_at']
            td = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(td,'%a %b %d %H:%M:%S +0000 %Y'))
            tweet_dt.append(td)
    df_new = pd.DataFrame({'tweet_dt': tweet_dt})
    df_new['tweet_dt'] = pd.to_datetime(df_new['tweet_dt'])
    df_new['politician'] = mp
    df = pd.concat([df, df_new])
    
#%%
    
def parlimentary_week_classifier(d):
    if d >= sitting_week_start and d < sitting_week_end:
        return 'Sitting week'
    elif d >= electorate_week_start and d < electorate_week_end:
        return 'Non-sitting week'
    else: 
        return 'out_of_range'
    
df['parliament_status'] = df['tweet_dt'].apply(lambda x: parlimentary_week_classifier(x))

#%%

df = df.loc[df['parliament_status'] != 'out_of_range']
df2 = pd.DataFrame({'politician': mps + mps, 'tweet_dt': ['Sitting week']*len(mps) + ['Non-sitting week']*len(mps), 'parliament_status': [0]*2*len(mps)})
res = df.groupby(['politician', 'parliament_status'])['tweet_dt'].count().reset_index()
res2 = pd.DataFrame({'politician': mps + mps, 'parliament_status': ['Sitting week']*len(mps) + ['Non-sitting week']*len(mps), 'tweet_dt': [0]*2*len(mps)})
res = pd.concat([res, res2])
res = res.sort_values(by = ['tweet_dt'], ascending = False)
res = res.drop_duplicates(subset = ['politician', 'parliament_status'])
res.boxplot(by = 'parliament_status', column = ['tweet_dt'])

res_ew = res.loc[res['parliament_status'] == 'Non-sitting week']
print(res_ew.describe())
res_sw = res.loc[res['parliament_status'] == 'Sitting week']
print(res_sw.describe())

res.to_csv('twitter_results.csv', index = False)
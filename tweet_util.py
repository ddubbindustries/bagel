import json, csv
from cfg import *
from TwitterSearch import *

def get_tweet_archive(filename):
	reader = csv.DictReader(open(filename, 'rb'))
	arr = []
	for line in reader:
		arr.append(line)
	print('getting tweets from archive:', len(arr))
	return {'statuses': arr}

def TwitterInit():
	key = cfg['txtzr']
	return TwitterSearch(
		consumer_key = key['consumer_key'], 
		consumer_secret = key['consumer_secret'], 
		access_token = key['token'], 
  	access_token_secret = key['token_secret']
	)

def get_tweets(tso, count, max_queries = 10):
	ts = TwitterInit()
	try:
		out = {
			'search_metadata': {},
			'statuses': []
		}

		current_count = 0
		for tweet in ts.search_tweets_iterable(tso):
			out['statuses'].append(tweet)
			current_count += 1
			if ts.get_statistics()[0] > max_queries or current_count >= count:
				break

		#out = ts.search_tweets(tso)['content']
		print("Queries done: %i. Tweets received: %i" % ts.get_statistics())
	
		meta = ts.get_metadata()
		limit = float(meta['x-rate-limit-limit'])
		remaining = float(meta['x-rate-limit-remaining'])
	
		out['search_metadata']['rate-limit-percent'] = remaining / limit
		out['statuses'] = [s for s in out['statuses'] if not s.get('possibly_sensitive', False)]
		print('tweets sent: ', len(out['statuses']))
		return out

	except TwitterSearchException as e: 
	  print(e)

def search_tweets(query, count=300, popular=False):
	if query[0] == '"' and query[-1] == '"':
		query = [query]
	else:
		query = query.split(' ')

	print('getting search tweets', query, count)
	tso = TwitterSearchOrder() 
	tso.set_keywords(query) 
	#tso.set_language('en')
	if (popular): tso.set_result_type('popular')  #only returns 15 results
	#tso.set_include_entities(False)
	return get_tweets(tso, count)

def user_tweets(username, count=15):
	print('getting user tweets', username, count)
	tuo = TwitterUserOrder(username) 
	return get_tweets(tuo, count)

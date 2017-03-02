from bottle import get, post, hook, request, response, route, run, redirect, template, static_file
from nltk_util import *
from tweet_util import *

@hook('after_request')
def enable_cors():
	response.set_header('Access-Control-Allow-Origin', '*')
	response.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
	response.set_header('Cache-Control', 'max-age=3600,public')

@route('/')
def reindex():
	redirect('/index.html')

@route('/search/<query>')
def search_output(query):
	return search_tweets(query)

@route('/search/<query>/<count:int>')
def search_output(query, count):
	return search_tweets(query, count)

@route('/user/<username>')
def user_output(username):
	if username == '_ddubb': 
		print 'getting tweets from cached csv archive'
		return get_tweet_archive('data/csv/_ddubb.csv') 
	elif username == 'realdonaldtrump':
		print 'getting tweets from cached json'
		return static_file(username+'.json', root='./data/json/')
	else:
		return user_tweets(username)

@route('/nlp/synonyms/<word>')
def syn_output(word):
	return get_synonyms(word)

@route('/nlp/wordnet/<word>')
def nlp_wordnet(word):
	return get_wordattributes(word)

@route('/nlp/freq', method='POST')
def process():
	res = request.body.read()
	return get_freq(res)

@route('/<filename:path>')
def server_static(filename):
	return static_file(filename, root='./')

run(host='localhost', port=8080)

import json, nltk, re
from nltk.tokenize import TweetTokenizer
from nltk.collocations import *
from nltk.corpus import stopwords, wordnet as wn
from nltk.util import ngrams
from collections import Counter

rejects = stopwords.words('english')
rejects.extend(['rt','/','!',':','.',',','-','...','"','@','(',')'])

def is_titlecase(s):	
	articles = ['a', 'an', 'and', 'of', 'the', 'is']
	word_list = re.split(' ', s.lower())
	final = [word_list[0].capitalize()]
	for word in word_list[1:]:
		final.append(word if word in articles else word.capitalize())
	return s == ' '.join(final)


def is_lowercase_hapax(item, arr):
	lower_arr = [i.lower() for i in arr]
	return item.islower() and lower_arr.count(item) == 1


def get_ngrams(ngram_count, tokens, corpus, score_method='raw_freq'):
	if ngram_count == 2:
		measure = nltk.collocations.BigramAssocMeasures()
		finder = BigramCollocationFinder.from_words(tokens)
	if ngram_count == 3: 
		measure = nltk.collocations.TrigramAssocMeasures()
		finder = TrigramCollocationFinder.from_words(tokens)
	
	finder.apply_freq_filter(3)
	finder.apply_word_filter(lambda w: len(w) < 3 or w.lower() in rejects or not w[0].isalnum())
	colloc = finder.score_ngrams(getattr(measure, score_method))	

	colloc = [' '.join(ngram[0]) for ngram in colloc]
	
	#make a set of best capitalizations
	#colloc = [i for i in colloc if is_titlecase(i) or is_lowercase_hapax(i, colloc)]
	
	out = [[ngram, corpus.count(ngram)] for ngram in colloc]
	return sorted(out, key=lambda i: i[1], reverse=True)

def get_ngrams2(ngram_count, tokens, num):
	#additional ngram filters
	filtered = [t for t in tokens if t.lower() not in rejects and t[0].isalnum()]
	ngram = Counter(ngrams(filtered, ngram_count)).most_common(num)
	return [(' '.join(n[0]), n[1]) for n in ngram]


def get_freq(corpus, result_count = 30, min_word_len = 3):
	corpus = unicode(corpus, "utf-8")	

	tknzr = TweetTokenizer()
	
	#make sets from sentences first, then tokenize
	tokens = []
	sents = corpus.split('\n\n')
	for sent in sents:
		sent_tokens = tknzr.tokenize(sent)
		sent_set = sorted(set(sent_tokens), key=sent_tokens.index)
		tokens.extend(sent_set)
	
	#tokens = tknzr.tokenize(corpus)
	filtered = [w.lower() for w in tokens if w.lower() not in rejects and len(w) >= min_word_len]
	print 'got {} tokens, {} unique, {} filtered'.format(
		len(tokens), len(set(tokens)), len(set(filtered))
	)
	text = nltk.Text(filtered)
	fdist = nltk.FreqDist(text).most_common(result_count)

	return json.dumps({
		'tokens': fdist,
		'bigrams': get_ngrams(2, tokens, corpus)[:5],
		'trigrams': get_ngrams(3, tokens, corpus)[:5],
	})

#from nltk.corpus import PlaintextCorpusReader
#corpus = PlaintextCorpusReader('./data/txt/','.*').raw('realdonaldtrump.txt')
#print get_freq(corpus)


def output(arr):
	return [item.replace('_',' ') for item in arr]


def get_synonyms(word):
	syn = wn.synsets(word)
	synonyms = []
	for s in syn:
		for lemma in s.lemma_names():
			synonyms.append(lemma)

	out = list(set(synonyms)-set([word]))
	return output(out)


def get_types(word):
	try:
		syn = wn.synsets(word)
		types_of_word = syn[0].hyponyms()
		return output([lemma.name() for synset in types_of_word for lemma in synset.lemmas()])
	except:
		return []


def get_taxonomy(word):
	try:
		syn = wn.synsets(word)
		paths = syn[0].hypernym_paths()
		taxonomy = [path.lemma_names()[0] for path in paths[0]]	
		taxonomy.reverse()
		return output(taxonomy[1:])
	except:
		return []


def get_definition(word):
	try:
		syn = wn.synsets(word)
		return syn[0].definition()
	except:
		return []


def get_wordattributes(word):	
	word = word.replace(' ','_')
	return {
		'synonyms': get_synonyms(word),
		'taxonomy': get_taxonomy(word),
		'types': get_types(word),
		'definition': get_definition(word)
	}

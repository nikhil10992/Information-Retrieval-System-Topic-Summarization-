from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from summarize import tweetModule
from aylienapiclient import textapi
import json, urllib.request, simplejson, re, wikipedia


YOUR_APP_ID='26cedfcc'
YOUR_APP_KEY='76f4731b3e7cac53411a5f17fe48d369'
aylienClient = textapi.Client(YOUR_APP_ID, YOUR_APP_KEY)

# Index Page Population
@csrf_exempt
def index(request):
	return render(request, 'summarize/index.html')

@csrf_exempt
def detail(request, nArg):
	print("Det", nArg)
	with open('summarize/data/data.txt', 'r') as infile:
		data = json.load(infile)
	context = json.dumps(data)
	return HttpResponse(context, content_type='application/json')

def write(data):
	print("Writing")
	with open('summarize/data/data.txt', 'w') as outfile:
	    json.dump(data, outfile, indent=4, sort_keys=True)

def getSummaryAndSentiment(sText, topicDetailsDict):	 
	sText = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',"", sText)
	sText = re.sub(r"#(\w+)","", sText)
	sText = re.sub('(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)',"", sText)
	sText = sText.encode('utf-8')

	test = sText
	summary = aylienClient.Summarize({'title':"summary" , 'text': test, 'sentences_number': 3, 'language':"en"})

	stringSummary = ""
	# for sentence in summary['sentences']:
	# 	stringSummary = stringSummary + sentence
	topicDetailsDict['tweetSummary'] = summary['sentences']
	
	text = sText
	sentiment = aylienClient.Sentiment({'text': text})
	percent = sentiment['polarity_confidence'] * 100
	emotion = sentiment['polarity']

	emotionPercentage = {}
	emotionPercentage[emotion] = percent
	topicDetailsDict['sentiment'] = emotionPercentage

def getWikiSummaryAndRelatedPhrases(label, topicDetailsDict):

	label = int(label)
	wikipedia.set_lang("en")
	wikiSummary = ""
	relatePhrases = []
	if label == 0:
		wikiSummary = wikipedia.summary("Christmas_dinner", sentences=5)
		related = aylienClient.Related({"phrase": "Christmas dinner"})
		for phrase in related['related']:
			relatePhrases.append(phrase['phrase'])
	elif label == 1:
		wikiSummary = wikipedia.summary("Christmas_carol",sentences=5)
		related = aylienClient.Related({"phrase": "Christmas carol"})
		for phrase in related['related']:
			relatePhrases.append(phrase['phrase'])
	elif label == 2:
		wikiSummary = wikipedia.summary("Hanukkah",sentences=5)
		related = aylienClient.Related({"phrase": "Hanukkah"})
		for phrase in related['related']:
			relatePhrases.append(phrase['phrase'])
	elif label == 3:
		wikiSummary = wikipedia.summary("Santa_Claus",sentences=5)
		related = aylienClient.Related({"phrase": "Santa Claus"})
		for phrase in related['related']:
			relatePhrases.append(phrase['phrase'])
	elif label == 4:
		wikiSummary = wikipedia.summary("Gift", sentences=5)
		related = aylienClient.Related({"phrase": "Gift"})
		for phrase in related['related']:
			relatePhrases.append(phrase['phrase'])
	elif label == 5:
		wikiSummary = wikipedia.summary("Christmas_carol",sentences=5)
		related = aylienClient.Related({"phrase": "Christmas carol"})
		for phrase in related['related']:
			relatePhrases.append(phrase['phrase'])

	topicDetailsDict['relatedPhrases'] = relatePhrases
	topicDetailsDict['wikiSummary'] = wikiSummary

@csrf_exempt
def populateData(request, nArg):
	print("Pop", nArg)
	finalStructure = {}
	labelAndCount = {}
	labelAndTopics = {}

	for label in range(6):
		label = str(label)
		lableURL = "http://54.202.209.219:8983/solr/core1/select?indent=on&q=label:" + label + "&rows=0&wt=json"
		labelResponse = urllib.request.urlopen(lableURL)
		labelData = simplejson.load(labelResponse)
		labelAndCount[label] = labelData['response']['numFound']

		topicURL = "http://54.202.209.219:8983/solr/core1/select?fl=topics&indent=on&q=label:" + label + "&rows=1&wt=json"
		topicResponse = urllib.request.urlopen(topicURL)
		topicData = simplejson.load(topicResponse)
		labelAndTopics[label] = topicData['response']['docs'][0]['topics']


	for label in labelAndTopics.keys():
		topicDetailsDict = {}
		topicDetailsDict['totalTweets'] = labelAndCount[label]

		topics = labelAndTopics[label]
		topicDetailsDict["topics"] = topics
		topTweetsURL = "http://54.202.209.219:8983/solr/core1/select?indent=on&q=text_1:%20" + topics[0] + "%20OR%20text_1:%20" + topics[1] + "&rows=15&wt=json"
		topTweetsResponse = urllib.request.urlopen(topTweetsURL)
		topTweetsData = simplejson.load(topTweetsResponse)
		counter = 0
		topTweetDetailsDict = {}
		sText = ""
		for doc in topTweetsData['response']['docs']:
			if counter < 5:
				tweetDetailsDict = {}
				tweetDetailsDict['created_at'] = doc['created_at']
				tweetDetailsDict['screen_name'] = doc['screen_name']
				tweetDetailsDict['tweet_text'] = doc['text']
				tweetDetailsDict['profile_image_url'] = doc['profile_image_url']
				tid = doc['id']
				topTweetDetailsDict[tid] = tweetDetailsDict
				counter += 1
			sText = sText + doc['text_1']

		getSummaryAndSentiment(sText, topicDetailsDict)

		getWikiSummaryAndRelatedPhrases(label, topicDetailsDict)

		topWordsAndCount = {}
		field = "text_" + label 
		topWordCounturl = "http://54.202.209.219:8983/solr/core1/terms?terms.fl=" + field + "&terms.sort=count&wt=json"
		topWordCountResponse = urllib.request.urlopen(topWordCounturl)
		topWordCountData = simplejson.load(topWordCountResponse)
		topWordsList = topWordCountData['terms'][field]
		topWordsAndCount = {}
		for i in range(0, 9, 2):
			key = topWordsList[i]
			topWordsAndCount[key] = topWordsList[i + 1]
		topicDetailsDict['topWords'] = topWordsAndCount

		countryAndCount = {}
		countryCountURL = "http://54.202.209.219:8983/solr/core1/select?fl=country_code&indent=on&q=label%20:%20" + label + "%20AND%20country_code:[*%20TO%20*]&rows=1000&wt=json"
		countryCountResponse = urllib.request.urlopen(countryCountURL)
		countryCountData = simplejson.load(countryCountResponse)
		for doc in countryCountData['response']['docs']:
			code = doc['country_code'][0]
			if code in countryAndCount.keys():
				countryAndCount[code] += 1
			else:
				countryAndCount[code] = 1

		topicDetailsDict['countryCount'] = countryAndCount
		topicDetailsDict['topTweets'] = topTweetDetailsDict	
		
		finalStructure[label] = topicDetailsDict

		write(finalStructure)
	return render(request, 'summarize/index.html')
class Tweet():
	def __init__(self, id, topic, tweet_lang, tweet_date, tweet_text = None, tweet_urls = None, text_en = None, **other_kwargs):
		self.tweet_id =  id
		self.tweet_text = tweet_text
		self.topic = topic
		self.tweet_lang = tweet_lang
		self.tweet_urls = tweet_urls
		self.tweet_date = tweet_date
		self.text_en = text_en
		self.other_kwargs = other_kwargs

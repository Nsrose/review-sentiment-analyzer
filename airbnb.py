import requests
from models import *

AIRBNB_API_URL = "https://airbnb19.p.rapidapi.com/api/v1/"
AIRBNB_API_KEY = "1ec0438affmsh25e64f02c10068ep18fb12jsn900feee46bfb"

PRESTON_PROPERTY_ID = 31609555


def get_reviews(propertyid):
	params = {
		"propertyId" : str(propertyid),
		"totalRecords": "40"
	}
	url = AIRBNB_API_URL + "getPropertyReviews"

	headers = {
		"X-RapidAPI-Key": AIRBNB_API_KEY,
		"X-RapidAPI-Host": "airbnb19.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers, params=params)

	return response.json()['data']

def reviews_to_comments(reviews):
	return [x['comments'] for x in reviews]

def reviews_to_prompt(reviews):
	all_comments = reviews_to_comments(reviews)
	textstring = '\n'.join(f'"{item}"' for item in all_comments)
	prompt = PROMPT_START + textstring
	prompt = prompt + "\n\n##\n\n"

	return prompt


def classify_review(comment):
	openai_response = openai_complete(comment, prompt_start="Find anything negative mentioned in this review:\n\n")
	response_text = openai_response.get('choices')[0].text.strip("\n")
	return response_text

def classify_reviews(reviews):
	comments = reviews_to_comments(reviews)
	result = []
	for i in range(len(comments)):
		result.append({
			"text" : comments[i],
			"sentiment" : classify_review(comments[i])
			})
	return result


def classify_property_reviews(propertyid):
	reviews = get_reviews(propertyid)
	return classify_reviews(reviews)


def summarize_reviews(review_classifications):
	review_classifications_sentiment_only = [x['sentiment'] for x in review_classifications]
	s = set(review_classifications_sentiment_only)

	# clean up the classifications and remove anything not negative
	if 'N/A' in s:
		s.remove('N/A')
	elif 'There is nothing negative mentioned in this review.' in s:
		s.remove('There is nothing negative mentioned in this review.')

	new_set = {item.strip('"') for item in s}
	text = "{}".format(' '.join(new_set))

	openai_response = openai_summarize(text)
	response_text = openai_response.get('choices')[0].text.strip('\n')
	return response_text


def summarize_airbnb_property(propertyid):
	review_classifications = classify_property_reviews(propertyid)
	summarization = summarize_reviews(review_classifications)
	return summarization
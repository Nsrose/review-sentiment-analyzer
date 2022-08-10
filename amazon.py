from xml.dom import HierarchyRequestErr
import requests
from openai_interface import *

import pdb


API_URL = "https://amazon24.p.rapidapi.com/api/"
RAPID_API_KEY = "1ec0438affmsh25e64f02c10068ep18fb12jsn900feee46bfb"

EXAMPLE_PRODUCT_ID = "B0827H4PYX"

def get_reviews(ProductID):
    querystring = {"page":"1","country":"US","sortBy":"helpful"}
    url = API_URL + "review/" + ProductID
    headers = {
		"X-RapidAPI-Key": RAPID_API_KEY,
		"X-RapidAPI-Host": "amazon24.p.rapidapi.com"
	}
    response = requests.get(url, headers=headers, params=querystring)

    data = {}
    json = response.json()

    data = {
        "reviews" : json['docs'],
        "overview" : json['overview'],
        "hasNextPage" : json['hasNextPage'],
        "hasPrevPage" : json['hasPrevPage'],
        "nextPage" : json["nextPage"]
    }
    
    if json['hasNextPage']:

        next_params = {
            "page" : json['nextPage'],
            "country" : "US",
            "sortBy" : "helpful"
        }
        response2 = requests.get(url, headers=headers, params=next_params)
        json2 = response2.json()

        next_review_set = json2['docs']
        prev_review_set = data['reviews']

        data["reviews"].extend(json2['docs'])

    return data["reviews"]

def reviews_to_comments(reviews):
	return [x['text'] for x in reviews]

def summarize_amazon_product(ProductID):
	reviews = get_reviews(ProductID)
	comments = reviews_to_comments(reviews)
	text = ' '.join(comments)
	prompt = "Here are several reviews for a product on Amazon. What do people not like about this product?"
	response = openai_summarize(text, prompt, completion_start="Summary:")
	return response.get('choices')[0].text.strip('\n')



def answer_question(ProductID, question):
	reviews = get_reviews(ProductID)
	comments = reviews_to_comments(reviews)
	text = ' '.join(comments)
	prompt = "Here are several reviews for an Amazon product. "
	prompt += question

	response = openai_summarize(text, prompt, completion_start="Answer:")
	return response.get('choices')[0].text.strip('\n')
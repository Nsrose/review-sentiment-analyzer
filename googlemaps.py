import requests
from openai_interface import *

GOOGLEMAPS_API_URL = "https://maps.googleapis.com/maps/api/"
GOOGLEMAPS_API_KEY = "AIzaSyAhkiMlH0uf6DG0CROWYnqw3YsWkzPzkUo"

YELP_API_URL = "https://api.yelp.com/v3"
YELP_API_KEY = "nCA5WDkiBNyyd7JWZELNVH2aM3bYMBpnnFklAuly659M8HSkmH3gmDEBvjPeNgmoK7qvwKJJRgenviGXzBbT121Zo2lJkM5N0bGshQ_lQNJDvAp5__3uECc5lHq7YnYx"

BIRITE_CREAMERY = "ChIJh1wqPBh-j4ARliLVoyr5W_c"

def get_reviews(PlaceID):
	url = GOOGLEMAPS_API_URL + "place/details/json?place_id=" + PlaceID + "&key=" + GOOGLEMAPS_API_KEY

	response = requests.get(url)

	return response.json()['result']['reviews']


def reviews_to_comments(reviews):
	return [x['text'] for x in reviews]
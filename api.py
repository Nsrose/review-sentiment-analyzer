from flask import Flask, request, jsonify
from flask_api import status
import openai
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from langdetect import detect
from openai_interface import *
from airbnb import *
from models import *


app = Flask(__name__)


limiter = Limiter(app, key_func=get_remote_address)




@app.route('/negativity_finder/', methods=['POST'])
@limiter.limit("3/minute")
def negativity_finder():
    content = request.get_json()
    text = content.get("text", None)

    response = {}

    ## Validations ##

    if not text:
        return "No review text found. Please supply the 'text' directly in the request body.", status.HTTP_400_BAD_REQUEST
    elif detect(text) != "en":
        return "Unsupported language. Right now only English is supported.", status.HTTP_400_BAD_REQUEST

    ## passed validation ## 

    else:
        openai_response = openai_complete(text, prompt_start="Find anything negative mentioned in this review:\n\n")
        response_text = openai_response.get('choices')[0].text.strip("\n")
        response['Review text'] = text
        response['Sentiment'] = response_text
        return jsonify(response)



@app.route('/negativity_finder/airbnb/<PropertyID>', methods=["POST"])
@limiter.limit("3/minute")
def airbnb_negativity_finder_by_property(PropertyID):
    summarize = request.args.get('summarize', None)
    debug = request.args.get('debug', None)


    if debug:
        review_classifications = classify_property_reviews(PropertyID)
        review_classifications_sentiment_only = [x['sentiment'] for x in review_classifications]
        s = set(review_classifications_sentiment_only)
        if 'N/A' in s:
            s.remove('N/A')
        elif 'There is nothing negative mentioned in this review.' in s:
            s.remove('There is nothing negative mentioned in this review.')

        new_set = {item.strip('"') for item in s}
        text = "{}".format(' '.join(new_set))
        prompt = "Summarize this review in 1 sentence:\n\n"
        prompt += "'{}'".format(text) + '\n\n\n\n'
        response_data = {}
        response_data["prompt"] = prompt
        response_data["review_classifications"] = review_classifications
        response_data["summary"] = openai.Completion.create(
              model="text-davinci-002",
              prompt=prompt,
              temperature=0,
              max_tokens=100,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0
            ).get('choices')[0].text.strip('\n')
        return jsonify(response_data)

    elif summarize:
        
        result = summarize_airbnb_property(PropertyID)
        return jsonify(result)



    return jsonify(classify_property_reviews(PropertyID))




@app.route('/')
def index():
    # A welcome message to test our server
    return "<h1>Welcome to the Review Sentiment Analyzer API</h1>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
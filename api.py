from flask import Flask, request, jsonify
from flask_api import status
import openai
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from langdetect import detect

app = Flask(__name__)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

limiter = Limiter(app, key_func=get_remote_address)


def openai_complete(comment, prompt_start):
    openai.api_key = OPENAI_API_KEY
    prompt = prompt_start
    prompt += 'Text: "{}"'.format(comment) + '\n\n'
    prompt += "Label: "

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0,
        max_tokens=512,
        top_p=1,
        frequency_penalty=1.9,
        presence_penalty=1.7
        )
    return response


@app.route('/negativity_finder/', methods=['POST'])
@limiter.limit("3/minute")
def respond():
    text = request.form.get("text", None)

    response = {}

    ## Validations ##

    if not text or detect(text) != "en":
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




@app.route('/')
def index():
    # A welcome message to test our server
    return "<h1>Welcome to the Review Sentiment Analyzer API</h1>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
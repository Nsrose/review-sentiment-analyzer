from flask import Flask, request, jsonify
from flask_api import status
import openai
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from langdetect import detect
from openai_interface import *
import airbnb, amazon
from models import *
from flask_cors import CORS
import requests
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
import json
from flask import Flask
from flask_caching import Cache



config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'
}

app = Flask(__name__)
app.config.from_mapping(config)
db.init_app(app)
ma = Marshmallow(app)
api = Api(app) 
cache = Cache(app)



class AirbnbComparisonSessionSchema(ma.Schema):
    class Meta:
        fields = ("id", "airbnbDetails")
        model = AirbnbComparisonSession




airbnb_comparison_session_schema = AirbnbComparisonSessionSchema()
airbnb_comparison_sessions_schema = AirbnbComparisonSessionSchema(many=True)

class AirbnbComparisonSessionListResource(Resource):
    def get(self):
        airbnb_comparison_sessions = AirbnbComparisonSession.query.all()
        return airbnb_comparison_sessions_schema.dump(airbnb_comparison_sessions)

    def post(self):
        request_dict = request.json["AirbnbDetails"]
        session_string = json.dumps(request_dict)

        new_session = AirbnbComparisonSession(
            airbnbDetails=session_string
        )
        db.session.add(new_session)
        db.session.commit()
        return airbnb_comparison_session_schema.dump(new_session)


class AirbnbComparisonSessionResource(Resource):
    def get(self, session_id):
        session = AirbnbComparisonSession.query.get_or_404(session_id)
        return airbnb_comparison_session_schema.dump(session)

api.add_resource(AirbnbComparisonSessionResource, '/airbnbcomparisonsessions/<int:session_id>')
api.add_resource(AirbnbComparisonSessionListResource, '/airbnbcomparisonsessions/')

with app.app_context():
    db.create_all()






CORS(app)

limiter = Limiter(app, key_func=get_remote_address)

@cache.memoize(1000)
def get_answer(text, question):
    answer = openai_answer(question, text, completion_start="Answer:").get('choices')[0].text.strip('\n')
    return jsonify({
        "question" : question,
        "answer" : answer
    })

@app.route('/qna/', methods=["POST"])
# @limiter.limit("1/minute")
def qna():
    content = request.get_json()
    text = content.get("text", None)
    question = content.get("question", None)

    if not text:
        return "No text found. Please supply the 'text' directly in the request body.", status.HTTP_400_BAD_REQUEST
    elif not question:
        return "No question found. Please supply the 'question' directly in the request body.", status.HTTP_400_BAD_REQUEST

    return get_answer(text, question)
    # answer = openai_answer(question, text, completion_start="Answer:").get('choices')[0].text.strip('\n')
    # return jsonify({
    #     "question" : question,
    #     "answer" : answer
    # })


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
        review_classifications = airbnb.classify_property_reviews(PropertyID)
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
        
        result = airbnb.summarize_airbnb_property(PropertyID)
        return jsonify(result)



    return jsonify(airbnb.classify_property_reviews(PropertyID))


@app.route('/qna/airbnb/<PropertyID>', methods=["POST"])
@limiter.limit("3/minute")
def qna_airbnb(PropertyID):
    question = request.args.get('question', None)

    if not question:
        response = "Please supply a question as part of the request arguments."
        return response, status.HTTP_400_BAD_REQUEST


    if question[-1] != "?":
        question += "?"

    answer = airbnb.answer_question(PropertyID, question)

    return jsonify({
        "question" : question,
        "answer" : answer
        })


@app.route('/negativity_finder/amazon/<ProductID>', methods=["POST"])
@limiter.limit("3/minute")
def negativity_finder_amazon(ProductID):
    result = amazon.summarize_amazon_product(ProductID)
    return jsonify(result)

@app.route('/qna/amazon/<ProductID>', methods=["POST"])
@limiter.limit("3/minute")
def qna_amazon(ProductID):
    question = request.args.get('question', None)

    if not question:
        response = "Please supply a question as part of the request arguments."
        return response, status.HTTP_400_BAD_REQUEST


    if question[-1] != "?":
        question += "?"

    answer = amazon.answer_question(ProductID, question)

    return jsonify({
        "question" : question,
        "answer" : answer
        })

@cache.memoize(timeout=10000)
def get_unshortened_url(shortURL):
    url = "https://unshorten.me/s/" + shortURL

    longURL = requests.get(url).text.strip('\n')
    return jsonify(longURL)


@app.route('/util/airbnb/unshorten', methods=["POST"])
def unshorten_airbnb():
    content = request.get_json()
    shortURL = content.get("shortURL", None)
    return get_unshortened_url(shortURL)





@app.route('/')
def index():
    # A welcome message to test our server
    return "<h1>Welcome to the Review Sentiment Analyzer API</h1>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
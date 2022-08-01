from flask import Flask, request, jsonify
import openai

app = Flask(__name__)
OPENAI_API_KEY = "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"



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
        frequency_penalty=0,
        presence_penalty=0
        )
    return response


@app.route('/negativity_finder/', methods=['POST'])
def respond():
    text = request.form.get("text", None)

    response = {}

    if not text:
        response["ERROR"] = "No review text found. Please supply the text of the review in the request body".
    else:
        openai_response = openai_complete(text, prompt_start="Find anything negative mentioned in this review:\n\n")
        response_text = openai_response.get('choices')[0].text.strip("\n")
        response['Review text'] = text
        response['Sentiment'] = response_text


    # Return the response in json format
    return jsonify(response)




@app.route('/')
def index():
    # A welcome message to test our server
    return "<h1>Welcome to the Review Sentiment Analyzer API</h1>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
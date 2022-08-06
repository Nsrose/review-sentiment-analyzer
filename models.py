import openai
import os


OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


def openai_complete(comment, prompt_start, completion_start="Label: "):
    openai.api_key = OPENAI_API_KEY
    prompt = prompt_start
    prompt += 'Text: "{}"'.format(comment) + '\n\n\n\n'
    prompt += completion_start

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


def openai_summarize(text):
	openai.api_key = OPENAI_API_KEY
	prompt = "Summarize this review in 1 sentence:\n\n"
	prompt += "'{}'".format(text) + '\n\n\n\n'


	response = openai.Completion.create(
	  model="text-davinci-002",
	  prompt=prompt,
	  temperature=0,
	  max_tokens=100,
	  top_p=1,
	  frequency_penalty=0,
	  presence_penalty=0
	)
	return response
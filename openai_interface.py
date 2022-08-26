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


def openai_summarize(text, prompt, completion_start="", temperature=0, max_tokens=200, top_p=1, frequency_penalty=0, presence_penalty=0):
	openai.api_key = OPENAI_API_KEY
	prompt += "\n\n"
	prompt += '"{}"'.format(text)  + "\n\n##\n\n"
	prompt += completion_start

	return openai.Completion.create(
		model='text-davinci-002',
		prompt=prompt,
		temperature=temperature,
		max_tokens=max_tokens,
		top_p=top_p,
		frequency_penalty=frequency_penalty,
		presence_penalty=presence_penalty
		)


def openai_answer(question, text, extra_context="", temperature=0, max_tokens=100, completion_start=""):
    openai.api_key = OPENAI_API_KEY
    prompt = extra_context + '\n\n'
    prompt += text + "\n\n"
    prompt += question + '\n\n##\n\n'
    prompt += completion_start

    return openai.Completion.create(
        model='text-davinci-002',
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )


def openai_classify_humblebrag(text):
    openai.api_key = OPENAI_API_KEY
    prompt="Decide whether a LinkedIn post's sentiment is bragging or not bragging.\n\nPost: \"I gained 5M followers over the course of 2 months. Here's how:\"\nSentiment: Bragging\n\nPost: \"Humbled & excited to announce that I've just accepted an offer to join Google as a software engineer.\"\nSentiment: Bragging\n\nPost: \"Learned a lot from this livestream session on how to improve your site's checkout conversion\"\nSentiment: Not bragging\n\nPost: \"Now I'm out of school and solving problems most people choose not to address because it's simply human nature to take the path of least resistance. Are you ready for what I'm about to do? Because I am.\"\nSentiment: Bragging\n\n"
    prompt += "Post: \"" + text + "\"\nSentiment: \n"
    return openai.Completion.create(
        model="text-curie-001",
        prompt=prompt,
        temperature=0,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0
    )
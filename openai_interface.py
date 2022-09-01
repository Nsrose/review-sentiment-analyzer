import openai
import os
import pandas as pd
import json



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




def fine_tune_humblebrag(csv_file):
    df = pd.read_csv(csv_file)

    def number_to_label(number):
        if number == 0:
            return " humble"
        return " bragging"  
    df.completion = df.completion.apply(number_to_label)
    df.prompt = df.prompt.apply(lambda p: p + "\n\n###\n\n")

    train_df = df.sample(frac=0.75)
    test_df = df.drop(train_df.index)


    train_df.to_json("humblebrag_train.jsonl", orient='records', lines=True)
    test_df.to_json("humblebrag_test.jsonl", orient='records', lines=True)

    openai.api_key = OPENAI_API_KEY
    train_file_id = openai.File.create(file=open("humblebrag_train.jsonl"), purpose='fine-tune').id
    test_file_id = openai.File.create(file=open("humblebrag_test.jsonl"), purpose='fine-tune').id
    return openai.FineTune.create(
        training_file=train_file_id,
        validation_file=test_file_id,
        compute_classification_metrics=True,
        classification_positive_class=" bragging"
    )


def get_accuracy_score(ft_id):
    openai.api_key = OPENAI_API_KEY
    FineTune = openai.FineTune.retrieve(ft_id)
    result_file_id = FineTune.result_files[0].id
    content = openai.File.download(result_file_id)
    with open("results.csv", "wb") as csv_file:
        csv_file.write(content)
    csv_file.close()
    df = pd.read_csv("results.csv")
    return df

def convert_json_export_to_csv(json_file_export, output_name="new_training_data.csv"):
    # Given a json file from Firebase, convert it into a CSV file equivalent to the one used in fine_tune_humblebrag (but do not merge)
    f = open(json_file_export)
    data = json.load(f)
    cleaned_data = []
    for key, value in data.items():
        cleaned_data.append(value)

    df = pd.DataFrame(cleaned_data)

    df = df[(df.label == 1.0) | (df.label == -1.0)] # only include the newer labelling system
    df = df[df.feedbackType == "bragging"] # only include the bragging feedback (not selling stuff)
    df = df.dropna()

    def label_corrector(extensionLabel, label):
        if extensionLabel:
            if label == 1.0:
                return 1
            else:
                return 0
        else:
            if label == 1.0:
                return 0
            else:
                return 1

    df["completion"] = df.apply(lambda row: label_corrector(row.extensionLabel, row.label), axis=1)
    df = df.rename(columns={"text" : "prompt"})
    df = df[["prompt", "completion"]]

    df.to_csv(output_name, index=False)

    return df
    



    




def openai_classify_humblebrag(text):
    openai.api_key = OPENAI_API_KEY
    prompt = text + "\n\n###\n\n"
    return openai.Completion.create(
        model="curie:ft-personal-2022-09-01-19-33-22",
        prompt=prompt,
        max_tokens=1,
        temperature=0
    )


    # prompt="Decide whether a LinkedIn post's sentiment is bragging or not bragging.\n\nPost: \"I gained 5M followers over the course of 2 months. Here's how:\"\nSentiment: Bragging\n\nPost: \"Humbled & excited to announce that I've just accepted an offer to join Google as a software engineer.\"\nSentiment: Bragging\n\nPost: \"Learned a lot from this livestream session on how to improve your site's checkout conversion\"\nSentiment: Not bragging\n\nPost: \"Now I'm out of school and solving problems most people choose not to address because it's simply human nature to take the path of least resistance. Are you ready for what I'm about to do? Because I am.\"\nSentiment: Bragging\n\n"
    # prompt += "Post: \"" + text + "\"\nSentiment: \n"
    # return openai.Completion.create(
    #     model="text-davinci-002",
    #     prompt=prompt,
    #     temperature=0,
    #     max_tokens=60,
    #     top_p=1,
    #     frequency_penalty=0.5,
    #     presence_penalty=0
    # )
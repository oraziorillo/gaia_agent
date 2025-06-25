import json
from dotenv import load_dotenv
import requests
load_dotenv(override=True)

from graph import graph

with open('questions.json', 'r') as f:
    questions = json.load(f)

hf_api_base_url = 'https://agents-course-unit4-scoring.hf.space'
question = requests.get(f'{hf_api_base_url}/random-question').json()['question']

messages = [
    (
        "user", question
    ),
]
response = graph.invoke({
    "messages": messages
})
answer = response['messages'][-1].content
print(f"### Question ###\n{question}\n\n### Answer ###\n{answer}")
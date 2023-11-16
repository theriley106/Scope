import os
from openai import OpenAI

API_KEY = os.environ.get('OPENAI_API_KEY')
if API_KEY == None:
    raise Exception("Text Chris to get the open api key if you're trying to run this locally")
client = OpenAI(api_key=API_KEY)


def fetch_openai_response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

START_PROMPT = """
You are an AI model by the name of ScopeAI that is trained to act a research assisant in a labratory setting. I will feed you the
contents of a file and you need to answer questions regarding the contents. 
You will response concisely from the perspective of a skilled researcher with a large amount of context
about the research being done in the labratory.

The file contents are as followed:
""".replace("\n", " ")

class ScopeAI():
    def __init__(self, file_contents):
        self.prompt = START_PROMPT + "\n" + file_contents + "\n"
        self.last = []

    def add_to_prompt(self, text):
        xr = "Researcher: " + text + "\nAI: "
        self.last.append(xr)
        self.prompt += xr

    def submit(self):
        # print(self.last[-1], end=" ")
        return fetch_openai_response(self.prompt)
    
def get_response_from_question(file_contents, question):
    A = ScopeAI(file_contents)
    A.add_to_prompt(question)
    return A.submit().strip()

if __name__ == "__main__":
    A = ScopeAI("testing")

    newPrompt = "test"

    while len(newPrompt) > 0:
        newPrompt = input("Client: ")
        A.add_to_prompt(newPrompt)
        print(A.submit())
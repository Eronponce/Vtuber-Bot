import openai

import creds
# Set your OpenAI API key

openai.api_key = creds.OPENAI_API_KEY
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def openai_chat_completion(conversation):
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = conversation,
        temperature= 0.7)
    return response.choices[0].message.content.strip()

# from openai import OpenAI
# # Point to the local server
# client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

# def open_file(filepath):
#     with open(filepath, 'r', encoding='utf-8') as infile:
#         return infile.read()
    
# def openai_chat_completion(conversation):

  
#     completion = client.chat.completions.create(
#     model="local-model", # this field is currently unused
#     messages=conversation,
#     temperature=0.7,
#     )

#     return completion.choices[0].message.content.strip()
    
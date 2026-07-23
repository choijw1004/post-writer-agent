import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

r = client.chat.completions.create(
    model="gpt-5.6-sol",
    messages=[{"role": "user", "content": "안녕? 한 문장으로 답해줘."}],
)
print(r.choices[0].message.content)
print("토큰:", r.usage.prompt_tokens, "/", r.usage.completion_tokens)
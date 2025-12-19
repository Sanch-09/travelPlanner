# from dotenv import load_dotenv
# import os

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize client
client = OpenAI(api_key=api_key)

# Test call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello, this is a test!"}]
)

print(response.choices[0].message.content)

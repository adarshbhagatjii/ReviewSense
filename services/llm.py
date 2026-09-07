import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(question, context):

    prompt = f"""
You are an Amazon customer review assistant.

Answer the user's question using ONLY
the provided customer reviews.

If the answer cannot be found in the reviews,
say that the information is not available.

Customer Reviews:

{context}

User Question:

{question}

Answer clearly and concisely.
"""


    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": "You answer questions using retrieved customer reviews."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )


    return response.choices[0].message.content
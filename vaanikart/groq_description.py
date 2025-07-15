import os
from dotenv import load_dotenv
import openai

load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def generate_product_description_groq(user_input):
    prompt = f"""
    Convert this raw product input into a clear, market-ready catalog listing.

    Input: {user_input}

    Format:
    Product Name: <name>
    Description: <description>
    Price:<price>
    Category:<Category>

    Keep it concise and attractive.
    """

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a product catalog assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Groq generation error:", e)
        return "Error generating product description."

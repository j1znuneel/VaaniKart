import os
import re
import json
from dotenv import load_dotenv
import openai

load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def generate_product_description_groq(user_input):
    """
    Generates product catalog entries from raw voice/text input.
    Returns list of products as JSON.
    Includes:
    - product_name
    - 2–3 sentence description
    - price ("Not provided" if missing)
    - quantity ("Not provided" if missing)
    - category (from fixed list)
    """

    system_prompt = """
You are a smart catalog assistant helping rural sellers describe their products clearly.

Instructions:
1. Only use one of the following fixed categories:
   Fruits, Vegetables, Spices, Grains, Oils, Dairy Products, Pickles, Snacks, Handicrafts, Utensils, Garments, Home Decor

2. If the input is NOT product-related (e.g. "My name is Arjun"), reply exactly:
   INVALID: Not a product

3. If there are MULTIPLE products in the input, return each in a separate JSON object.

4. If PRICE or QUANTITY is missing, set the field to "Not provided" (do not guess or suggest).

5. For each product, return this exact JSON structure (no code blocks or markdown):

[
  {
    "product_name": "string",
    "description": "2–3 sentence marketing-friendly description",
    "price": "₹value" or "Not provided",
    "quantity": "e.g. 1kg, 500ml, etc." or "Not provided",
    "category": "From the allowed list"
  },
  ...
]
"""

    prompt = f"User input: {user_input}"

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.7,
            max_tokens=400
        )

        content = response['choices'][0]['message']['content'].strip()
        
        # Handle irrelevant input
        if content.startswith("INVALID"):
            return {"error": "Not a product-related input."}

        # Clean code block if returned
        content = re.sub(r"^```json|^```|```$", "", content)

        parsed = json.loads(content)
        return parsed

    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON from model response."}
    except Exception as e:
        print("Groq generation error:", e)
        return {"error": "Something went wrong during generation."}

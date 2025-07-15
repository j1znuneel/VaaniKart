import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import os
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer

from decimal import Decimal
from .translation import translate_to_english
from .groq_description import generate_product_description_groq



load_dotenv()

LEMONFOX_KEY = os.getenv("LEMONFOX_KEY")
USER_LANGUAGE_PREFS = {}
USER_ACTION_STATE = {}


LANGUAGE_MAP = {
    "1": {"name": "English", "code": "en"},
    "2": {"name": "Hindi", "code": "hi"},
    "3": {"name": "Tamil", "code": "ta"},
}

def extract_media_url(media_id, access_token):
    print(f"🎧 Extracting media URL for media_id: {media_id}")
    url = f"https://graph.facebook.com/v19.0/{media_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print(f"🔗 Media URL Response: {response.status_code} {response.text}")
    if response.status_code == 200:
        return response.json().get("url")
    return None

def send_reply_to_user(user_number, message, access_token, phone_number_id):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": user_number,
        "type": "text",
        "text": {
            "body": message
        }
    }

    print("📤 Sending reply to user...")
    print("Payload:", json.dumps(data, indent=2))

    response = requests.post(url, headers=headers, json=data)

    print("📥 Meta API Response:")
    print("Status:", response.status_code)
    print("Response Body:", response.text)

    if response.status_code != 200:
        print("❌ Failed to send message. Check token, permissions, or payload format.")

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        verify_token = os.getenv("VERIFY_TOKEN", "vaanikart_hackathon")
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            print("✅ WEBHOOK_VERIFIED")
            return HttpResponse(challenge, status=200)
        else:
            print("❌ Webhook verification failed.")
            return HttpResponse("Verification failed", status=403)

    elif request.method == "POST":
        try:
            body = json.loads(request.body)
            print("=== 📩 Incoming Headers ===")
            print(dict(request.headers))
            print("=== 📦 Incoming Body ===")
            print(json.dumps(body, indent=2))

            entry = body["entry"][0]
            change = entry["changes"][0]
            value = change["value"]
            messages = value.get("messages", [])

            if not messages:
                print("ℹ️ No 'messages' found — skipping status-only update.")
                return JsonResponse({"status": "ignored - no user message"}, status=200)

            print("✅ Message received.")
            message = messages[0]
            user_number = message.get("from", "unknown")
            msg_type = message.get("type", "none")
            access_token = os.getenv("META_TOKEN")
            phone_number_id = os.getenv("META_PHONE_NUMBER_ID")

            if msg_type == "text":
                user_text = message["text"]["body"].strip().lower()
                print(f"✉️ Text Message: {user_text}")

                if user_text in ["hi", "hello", "hey"]:
                    USER_LANGUAGE_PREFS.pop(user_number, None)
                    USER_ACTION_STATE.pop(user_number, None)
                    intro = (
                        "👋 Welcome to *VaaniKart*, your voice-based catalog assistant!\n\n"
                        "I can help you create product listings using just your voice.\n\n"
                        "Please choose your language to get started:\n"
                        "1. 🇬🇧 English\n"
                        "2. 🇮🇳 Hindi\n"
                        "3. 🇮🇳 Tamil\n\n"
                        "Reply with *1*, *2*, or *3* to continue."
                    )
                    send_reply_to_user(user_number, intro, access_token, phone_number_id)

                elif user_text in LANGUAGE_MAP and user_number not in USER_LANGUAGE_PREFS:
                    USER_LANGUAGE_PREFS[user_number] = LANGUAGE_MAP[user_text]["code"]
                    USER_ACTION_STATE[user_number] = None
                    lang = LANGUAGE_MAP[user_text]
                    lang_code = lang["code"]
                    lang_name = lang["name"]

                    if lang_code == "en":
                        prompt = (
                            f"✅ Language set to *{lang_name}*.\n\n"
                            "What would you like to do?\n"
                            "1️⃣ Add Items\n"
                            "2️⃣ Remove Items\n"
                            "3️⃣ Update Items\n"
                            "4️⃣ View Items"

                        )
                    elif lang_code == "hi":
                        prompt = (
                            f"✅ भाषा *{lang_name}* में सेट की गई है।\n\n"
                           "आप क्या करना चाहेंगे?\n"
                            "1️⃣ आइटम जोड़ें\n"
                            "2️⃣ आइटम हटाएं\n"
                            "3️⃣ आइटम अपडेट करें\n"
                            "4️⃣ आइटम देखें"

                        )
                    elif lang_code == "ta":
                        prompt = (
                            f"✅ மொழி *{lang_name}* ஆக அமைக்கப்பட்டது.\n\n"
                            "நீங்கள் என்ன செய்ய விரும்புகிறீர்கள்?\n"
                            "1️⃣ பொருட்களைச் சேர்க்கவும்\n"
                            "2️⃣ பொருட்களை நீக்கவும்\n"
                            "3️⃣ பொருட்களை புதுப்பிக்கவும்\n"
                            "4️⃣ பொருட்களை காண்க"
                        )
                    else:
                        prompt = "✅ Language set. What would you like to do?"

                    send_reply_to_user(user_number, prompt, access_token, phone_number_id)

                elif user_text == "1":
                    USER_ACTION_STATE[user_number] = "add_item"
                    lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                    if lang_code == "hi":
                        reply = "🎙 कृपया जोड़ने के लिए वॉयस या टेक्स्ट भेजें।"
                    elif lang_code == "ta":
                        reply = "🎙 தயவுசெய்து சேர்க்க விரும்பும் உரை அல்லது குரலை அனுப்பவும்."
                    else:
                        reply = "🎙 Please send a voice note or text to add the item."
                    send_reply_to_user(user_number, reply, access_token, phone_number_id)
                elif user_text == "4":
                    try:
                        response = requests.get("http://127.0.0.1:8000/api/products/")  # Adjust to your backend domain if deployed
                        if response.status_code == 200:
                            products = response.json()
                            print(products
                                  )
                            if not products:
                                reply = "📦 No items found in your catalog."
                            else:
                                reply = "🛍️ *Your Items:*\n\n"
                                for product in products:
                                    reply += (
                                        f"🧾 *{product['name']}*\n"
                                        f"📄 {product['description']}\n"
                                        f"💰 Price: ₹{product['price']}\n"
                                        f"📦 Stock: {product['current_stock']}\n"
                                        f"🏷️ Category: {product['category'].capitalize()}\n\n"
                                    )
                        else:
                            reply = "⚠️ Couldn't fetch items at the moment. Please try again later."
                    except Exception as e:
                        print("❌ Error fetching products:", str(e))
                        reply = "⚠️ Failed to fetch products."

                    send_reply_to_user(user_number, reply, access_token, phone_number_id)

                else:
                    if USER_ACTION_STATE.get(user_number) == "add_item":
                        # Process the product input
                        process_product_input(user_number, user_text, access_token, phone_number_id)
                    else:
                        reply_text = user_text.upper()
                        send_reply_to_user(user_number, reply_text, access_token, phone_number_id)

            elif msg_type == "audio":
                print("🎤 Audio message detected.")
                media_id = message["audio"]["id"]
                print(f"🎧 Media ID: {media_id}")

                media_url = extract_media_url(media_id, access_token)
                if media_url is None:
                    print("❌ Could not get media URL.")
                    send_reply_to_user(user_number, "[Error: Couldn't access audio]", access_token, phone_number_id)
                    return JsonResponse({"status": "failed"}, status=500)

                print(f"⬇️ Downloading audio from: {media_url}")
                audio_resp = requests.get(media_url, headers={"Authorization": f"Bearer {access_token}"})
                print(f"📥 Audio Response: {audio_resp.status_code}")

                lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")

                print("🦊 Sending audio to Lemonfox for transcription...")
                lemon_response = requests.post(
                    "https://api.lemonfox.ai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {LEMONFOX_KEY}"},
                    files={"file": ("audio.ogg", audio_resp.content)},
                    data={"language": lang_code, "response_format": "text"}
                )

                print(f"🦊 Lemonfox Status: {lemon_response.status_code}")
                print("🦊 Lemonfox Response:", lemon_response.text)

                if lemon_response.status_code == 200:
                    transcript = lemon_response.text.strip()
                    
                    if USER_ACTION_STATE.get(user_number) == "add_item":
                        # Process the transcribed audio as product input
                        process_product_input(user_number, transcript, access_token, phone_number_id)
                    else:
                        response_msg = transcript
                        send_reply_to_user(user_number, response_msg, access_token, phone_number_id)
                else:
                    print("❌ Transcription failed")
                    send_reply_to_user(user_number, "[Error: Couldn't transcribe audio]", access_token, phone_number_id)

            else:
                print(f"❓ Unsupported message type: {msg_type}")

        except Exception as e:
            print("❗ Webhook processing error:", str(e))

        return JsonResponse({"status": "received"}, status=200)

    return HttpResponse(status=405)

def process_product_input(user_number, user_input, access_token, phone_number_id):
    """
    Process product input (text or transcribed audio) through translation and description generation,
    then save to database and send response to user.
    """
    try:
        lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
        
        # Translate to English if not already English
        if lang_code != "en":
            translated_text = translate_to_english(user_input)
            print(f"🌍 Translated text: {translated_text}")
        else:
            translated_text = user_input
        
        # Generate product description
        product_data = generate_product_description_groq(translated_text)
        
        if "error" in product_data:
            # Handle non-product input or generation error
            error_msg = product_data["error"]
            print(f"❌ {error_msg}")
            send_reply_to_user(user_number, f" {error_msg}", access_token, phone_number_id)
            return
        
        # Process each product in the response
        for product in product_data:
            # Save to database
            try:
                # Convert price from "₹100" to Decimal(100.00)
                price_str = product.get("price", "Not provided")
                if price_str != "Not provided":
                    price = Decimal(price_str.replace("₹", "").strip())
                else:
                    price = Decimal("0.00")
                
                # Convert quantity to stock count (simplified - you might want more sophisticated parsing)
                quantity_str = product.get("quantity", "Not provided")
                current_stock = 1 if quantity_str != "Not provided" else 0
                
                # Map category to our choices
                category_map = {
                    "Fruits": "fruits",
                    "Vegetables": "vegetables",
                    "Spices": "spices",
                    "Grains": "grains",
                    "Oils": "oils",
                    "Dairy Products": "dairy",
                    "Pickles": "pickles",
                    "Snacks": "snacks",
                    "Handicrafts": "handicrafts",
                    "Utensils": "utensils",
                    "Garments": "garments",
                    "Home Decor": "home_decor"
                }
                category = category_map.get(product["category"], "other")
                
                # Create and save product
                new_product = Product(
                    name=product["product_name"],
                    description=product["description"],
                    category=category,
                    price=price,
                    current_stock=current_stock,
                    is_available=True
                )
                new_product.save()
                
                # Prepare success message
                success_msg = (
                    f"✅ *{product['product_name']}* added successfully!\n\n"
                    f"*Description:* {product['description']}\n"
                    f"*Price:* {product.get('price', 'Not provided')}\n"
                    f"*Quantity:* {product.get('quantity', 'Not provided')}\n"
                    f"*Category:* {product['category']}"
                )
                
                # send_reply_to_user(user_number, success_msg, access_token, phone_number_id)
                lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")

                # Language-specific follow-up prompt
                if lang_code == "hi":
                    follow_up = (
                        "\n\nअब आप क्या करना चाहेंगे?\n"
                        "1️⃣ आइटम जोड़ें\n"
                        "2️⃣ आइटम हटाएं\n"
                        "3️⃣ आइटम अपडेट करें\n"
                        "4️⃣ आइटम एक्सपोर्ट करें"
                    )
                elif lang_code == "ta":
                    follow_up = (
                        "\n\nஇப்போது நீங்கள் என்ன செய்ய விரும்புகிறீர்கள்?\n"
                        "1️⃣ பொருட்களைச் சேர்க்கவும்\n"
                        "2️⃣ பொருட்களை நீக்கவும்\n"
                        "3️⃣ பொருட்களை புதுப்பிக்கவும்\n"
                        "4️⃣ பொருட்களை ஏற்றுமதி செய்யவும்"
                    )
                else:
                    follow_up = (
                        "\n\nWhat would you like to do next?\n"
                        "1️⃣ Add Items\n"
                        "2️⃣ Remove Items\n"
                        "3️⃣ Update Items\n"
                        "4️⃣ Export Items"
                    )

                send_reply_to_user(user_number, success_msg + follow_up, access_token, phone_number_id)

                
            except Exception as e:
                print(f"❌ Error saving product to database: {str(e)}")
                error_msg = f"⚠️ Failed to save product: {product['product_name']}"
                send_reply_to_user(user_number, error_msg, access_token, phone_number_id)
        
        # Reset action state
        USER_ACTION_STATE[user_number] = None
        
    except Exception as e:
        print(f"❌ Error processing product input: {str(e)}")
        send_reply_to_user(user_number, "⚠️ An error occurred while processing your request.", access_token, phone_number_id)

class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
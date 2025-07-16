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
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view




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

                # Handle "go back" option
                if user_text == "back" or user_text == "0":
                    USER_ACTION_STATE.pop(user_number, None)
                    lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                    
                    if lang_code == "hi":
                        reply = "🔙 मुख्य मेनू पर वापस आ गए। आप क्या करना चाहेंगे?\n\n1️⃣ आइटम जोड़ें\n2️⃣ आइटम हटाएं\n3️⃣ आइटम अपडेट करें\n4️⃣ आइटम देखें"
                    elif lang_code == "ta":
                        reply = "🔙 முதன்மை மெனுவுக்குத் திரும்பினார். நீங்கள் என்ன செய்ய விரும்புகிறீர்கள்?\n\n1️⃣ பொருட்களைச் சேர்க்கவும்\n2️⃣ பொருட்களை நீக்கவும்\n3️⃣ பொருட்களை புதுப்பிக்கவும்\n4️⃣ பொருட்களை காண்க"
                    else:
                        reply = "🔙 Back to main menu. What would you like to do?\n\n1️⃣ Add Items\n2️⃣ Remove Items\n3️⃣ Update Items\n4️⃣ View Items"
                    
                    send_reply_to_user(user_number, reply, access_token, phone_number_id)
                    return JsonResponse({"status": "processed"}, status=200)

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
                            "4️⃣ View Items\n\n"
                            "You can type *0* anytime to return to this menu."
                        )
                    elif lang_code == "hi":
                        prompt = (
                            f"✅ भाषा *{lang_name}* में सेट की गई है।\n\n"
                           "आप क्या करना चाहेंगे?\n"
                            "1️⃣ आइटम जोड़ें\n"
                            "2️⃣ आइटम हटाएं\n"
                            "3️⃣ आइटम अपडेट करें\n"
                            "4️⃣ आइटम देखें\n\n"
                            "आप कभी भी *0* टाइप करके इस मेनू पर वापस आ सकते हैं।"
                        )
                    elif lang_code == "ta":
                        prompt = (
                            f"✅ மொழி *{lang_name}* ஆக அமைக்கப்பட்டது.\n\n"
                            "நீங்கள் என்ன செய்ய விரும்புகிறீர்கள்?\n"
                            "1️⃣ பொருட்களைச் சேர்க்கவும்\n"
                            "2️⃣ பொருட்களை நீக்கவும்\n"
                            "3️⃣ பொருட்களை புதுப்பிக்கவும்\n"
                            "4️⃣ பொருட்களை காண்க\n\n"
                            "நீங்கள் எப்போது வேண்டுமானாலும் *0* என்று தட்டச்சு செய்து இந்த மெனுவுக்குத் திரும்பலாம்."
                        )
                    else:
                        prompt = "✅ Language set. What would you like to do?"

                    send_reply_to_user(user_number, prompt, access_token, phone_number_id)

                elif user_text == "1" and (USER_ACTION_STATE.get(user_number) or {}).get('action') != 'delete':

                    USER_ACTION_STATE[user_number] = "add_item"
                    lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                    if lang_code == "hi":
                        reply = "🎙 कृपया जोड़ने के लिए वॉयस या टेक्स्ट भेजें। (Type *0* to return)"
                    elif lang_code == "ta":
                        reply = "🎙 தயவுசெய்து சேர்க்க விரும்பும் உரை அல்லது குரலை அனுப்பவும். (*0* என தட்டச்சு செய்து திரும்பலாம்)"
                    else:
                        reply = "🎙 Please send a voice note or text to add the item. (Type *0* to return)"
                    send_reply_to_user(user_number, reply, access_token, phone_number_id)
                
                elif user_text == "2" and (USER_ACTION_STATE.get(user_number) or {}).get('action') != 'delete':

                    # Start deletion process
                    USER_ACTION_STATE[user_number] = {
                        "action": "delete",
                        "step": "list_products"
                    }
                    try:
                        response = requests.get("http://127.0.0.1:8000/api/products/")
                        if response.status_code == 200:
                            products = response.json()
                            if not products:
                                reply = "📦 No items found to delete."
                                USER_ACTION_STATE.pop(user_number, None)
                            else:
                                USER_ACTION_STATE[user_number]["products"] = products
                                lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                                
                                if lang_code == "hi":
                                    reply = "🗑️ हटाने के लिए आइटम नंबर चुनें:\n\n"
                                elif lang_code == "ta":
                                    reply = "🗑️ நீக்க விரும்பும் பொருளின் எண்ணைத் தேர்ந்தெடுக்கவும்:\n\n"
                                else:
                                    reply = "🗑️ Please choose the item number to delete:\n\n"
                                
                                for i, product in enumerate(products, start=1):
                                    reply += (
                                        f"{i}. *{product['name']}* — ₹{product['price']} "
                                        f"(Stock: {product['current_stock']})\n"
                                    )
                                
                                if lang_code == "hi":
                                    reply += "\nहटाने के लिए आइटम नंबर का जवाब दें। (वापस जाने के लिए *back* टाइप करें)"
                                elif lang_code == "ta":
                                    reply += "\nநீக்க பொருளின் எண்ணை பதிலளிக்கவும். (திரும்ப *back* தட்டச்சு செய்யவும்)"
                                else:
                                    reply += "\nReply with the item number to delete. (Type *back* to return)"
                        else:
                            lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                            if lang_code == "hi":
                                reply = "⚠️ उत्पाद प्राप्त नहीं कर सके। बाद में पुनः प्रयास करें।"
                            elif lang_code == "ta":
                                reply = "⚠️ பொருட்களைப் பெற முடியவில்லை. பின்னர் மீண்டும் முயற்சிக்கவும்."
                            else:
                                reply = "⚠️ Couldn't fetch products. Try again later."
                            USER_ACTION_STATE.pop(user_number, None)
                    except Exception as e:
                        print("❌ Error fetching products for deletion:", str(e))
                        lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                        if lang_code == "hi":
                            reply = "⚠️ उत्पादों को प्राप्त करने में त्रुटि हुई।"
                        elif lang_code == "ta":
                            reply = "⚠️ பொருட்களைப் பெறுவதில் பிழை ஏற்பட்டது."
                        else:
                            reply = "⚠️ Error fetching products."
                        USER_ACTION_STATE.pop(user_number, None)

                    send_reply_to_user(user_number, reply, access_token, phone_number_id)
                
                
                elif user_text == "4" and (USER_ACTION_STATE.get(user_number) or {}).get('action') != 'delete':

                    try:
                        response = requests.get("http://127.0.0.1:8000/api/products/")
                        if response.status_code == 200:
                            products = response.json()
                            print("📦 Products fetched:", products)

                            if not products:
                                reply = "📦 No items found in your catalog."
                            else:
                                lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                                if lang_code == "hi":
                                    lines = ["🛍️ *आपके आइटम:*"]
                                elif lang_code == "ta":
                                    lines = ["🛍️ *உங்கள் பொருட்கள்:*"]
                                else:
                                    lines = ["🛍️ *Your Items:*"]
                                
                                for product in products:
                                    # product_name_slug = product['name'].replace(" ", "-").lower()
                                    # product_url = f"https://vaani-kart.vercel.app/product/{product_name_slug}"
                                    lines.append(
                                        f"🧾 *{product['name']}*\n"
                                        f"📄 {product['description']}\n"
                                        f"💰 Price: ₹{product['price']}\n"
                                        f"📦 Stock: {product['current_stock']}\n"
                                        f"🏷️ Category: {product['category'].replace('_', ' ').title()}\n"
                                        # f"🔗 [View Product]({product_url})\n"
                                    )
                                reply = "\n".join(lines)
                                
                                # Add back option
                                if lang_code == "hi":
                                    reply += "\n\nवापस जाने के लिए *back* टाइप करें।"
                                elif lang_code == "ta":
                                    reply += "\n\nதிரும்ப *back* தட்டச்சு செய்யவும்."
                                else:
                                    reply += "\n\nType *back* to return."
                        else:
                            print(f"⚠️ API error {response.status_code}: {response.text}")
                            lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                            if lang_code == "hi":
                                reply = "⚠️ इस समय आइटम प्राप्त नहीं कर सके। कृपया बाद में पुनः प्रयास करें।"
                            elif lang_code == "ta":
                                reply = "⚠️ இப்போது பொருட்களைப் பெற முடியவில்லை. பின்னர் மீண்டும் முயற்சிக்கவும்."
                            else:
                                reply = "⚠️ Couldn't fetch items at the moment. Please try again later."

                    except Exception as e:
                        print("❌ Error fetching products:", str(e))
                        lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                        if lang_code == "hi":
                            reply = "⚠️ आंतरिक त्रुटि के कारण उत्पाद प्राप्त करने में विफल रहे।"
                        elif lang_code == "ta":
                            reply = "⚠️ உள் பிழை காரணமாக பொருட்களைப் பெறுவதில் தோல்வி."
                        else:
                            reply = "⚠️ Failed to fetch products due to an internal error."

                    send_reply_to_user(user_number, reply, access_token, phone_number_id)

                else:
                    current_state = USER_ACTION_STATE.get(user_number)
                    
                    if current_state == "add_item":
                        # Process the product input
                        process_product_input(user_number, user_text, access_token, phone_number_id)
                    
                    elif isinstance(current_state, dict) and current_state.get("action") == "delete":
                        if current_state.get("step") == "list_products":
                            try:
                                selected_index = int(user_text.strip())
                                products = current_state["products"]
                                
                                if 1 <= selected_index <= len(products):
                                    selected_product = products[selected_index - 1]
                                    current_state["step"] = "confirm_delete"
                                    current_state["selected_product"] = selected_product
                                    
                                    lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                                    product_name = selected_product["name"]
                                    
                                    if lang_code == "hi":
                                        reply = (
                                            f"क्या आप वाकई *{product_name}* को हटाना चाहते हैं?\n\n"
                                            "1. हाँ, हटाएं\n"
                                            "2. नहीं, रद्द करें\n\n"
                                            "या *back* टाइप करके वापस जाएं"
                                        )
                                    elif lang_code == "ta":
                                        reply = (
                                            f"நீங்கள் உண்மையில் *{product_name}* நீக்க விரும்புகிறீர்களா?\n\n"
                                            "1. ஆம், நீக்கவும்\n"
                                            "2. இல்லை, ரத்து செய்\n\n"
                                            "அல்லது *back* தட்டச்சு செய்து திரும்பவும்"
                                        )
                                    else:
                                        reply = (
                                            f"Are you sure you want to delete *{product_name}*?\n\n"
                                            "1. Yes, delete\n"
                                            "2. No, cancel\n\n"
                                            "Or type *back* to return"
                                        )
                                else:
                                    lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                                    if lang_code == "hi":
                                        reply = "⚠️ अमान्य चयन। कृपया एक वैध आइटम नंबर का जवाब दें।"
                                    elif lang_code == "ta":
                                        reply = "⚠️ தவறான தேர்வு. சரியான பொருள் எண்ணை பதிலளிக்கவும்."
                                    else:
                                        reply = "⚠️ Invalid selection. Please reply with a valid item number."
                            except ValueError:
                                lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                                if lang_code == "hi":
                                    reply = "⚠️ कृपया एक वैध संख्या का जवाब दें।"
                                elif lang_code == "ta":
                                    reply = "⚠️ தயவு செய்து சரியான எண்ணை பதிலளிக்கவும்."
                                else:
                                    reply = "⚠️ Please reply with a valid number."
                            
                            send_reply_to_user(user_number, reply, access_token, phone_number_id)
                        
                        elif current_state.get("step") == "confirm_delete":
                            if user_text == "1":  # Confirm delete
                                selected_product = current_state.get("selected_product")
                                if selected_product:
                                    product_name = selected_product["name"]
                                    delete_url = f"http://127.0.0.1:8000/api/products/delete-by-name/?name={product_name}"

                                    try:
                                        del_response = requests.delete(delete_url)
                                        print(f"🔍 Delete URL: {del_response.url}")
                                        print(f"🔍 Response Status: {del_response.status_code}")
                                        print(f"🔍 Response Text: {del_response.text}")
                                        if del_response.status_code == 200:
                                            lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                                            if lang_code == "hi":
                                                reply = f"✅ उत्पाद *{product_name}* सफलतापूर्वक हटा दिया गया।"
                                            elif lang_code == "ta":
                                                reply = f"✅ பொருள் *{product_name}* வெற்றிகரமாக நீக்கப்பட்டது."
                                            else:
                                                reply = f"✅ Product *{product_name}* deleted successfully."
                                        else:
                                            print(f"Delete API error: {del_response.status_code} - {del_response.text}")
                                            lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                                            if lang_code == "hi":
                                                reply = f"⚠️ *{product_name}* को हटाने में विफल। कृपया बाद में पुनः प्रयास करें।"
                                            elif lang_code == "ta":
                                                reply = f"⚠️ *{product_name}* நீக்குவதில் தோல்வி. பின்னர் மீண்டும் முயற்சிக்கவும்."
                                            else:
                                                reply = f"⚠️ Failed to delete *{product_name}*. Please try again later."
                                    except Exception as e:
                                        print("❌ Error deleting product:", str(e))
                                        lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                                        if lang_code == "hi":
                                            reply = "⚠️ हटाने के दौरान त्रुटि हुई।"
                                        elif lang_code == "ta":
                                            reply = "⚠️ நீக்கும் போது பிழை ஏற்பட்டது."
                                        else:
                                            reply = "⚠️ An error occurred during deletion."
                                    
                                    USER_ACTION_STATE.pop(user_number, None)
                                    send_reply_to_user(user_number, reply, access_token, phone_number_id)
                            
                            elif user_text == "2":  # Cancel delete
                                USER_ACTION_STATE.pop(user_number, None)
                                lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                                if lang_code == "hi":
                                    reply = "❌ हटाना रद्द कर दिया गया।"
                                elif lang_code == "ta":
                                    reply = "❌ நீக்குதல் ரத்து செய்யப்பட்டது."
                                else:
                                    reply = "❌ Deletion cancelled."
                                
                                send_reply_to_user(user_number, reply, access_token, phone_number_id)
                    
                    else:
                        # Default reply if no specific action is matched
                        lang_code = USER_LANGUAGE_PREFS.get(user_number, "en")
                        if lang_code == "hi":
                            reply = "मैं आपको समझ नहीं पाया। कृपया एक वैध विकल्प चुनें या *back* टाइप करें।"
                        elif lang_code == "ta":
                            reply = "நான் உங்களை புரிந்து கொள்ளவில்லை. சரியான விருப்பத்தைத் தேர்ந்தெடுக்கவும் அல்லது *back* தட்டச்சு செய்யவும்."
                        else:
                            reply = "I didn't understand that. Please select a valid option or type *back*."
                        
                        send_reply_to_user(user_number, reply, access_token, phone_number_id)

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
            # traceback.print_exc()  # Add this to get detailed error logs

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
    
    

@api_view(['DELETE'])
def delete_product_by_name(request):
    product_name = request.query_params.get("name")
    if not product_name:
        return Response({"error": "Product name is required."}, status=status.HTTP_400_BAD_REQUEST)

    products = Product.objects.filter(name__iexact=product_name)

    if not products.exists():
        return Response({"error": f"No product found with name '{product_name}'."}, status=status.HTTP_404_NOT_FOUND)

    count = products.count()
    products.delete()

    return Response({"message": f"Deleted {count} product(s) named '{product_name}'."}, status=status.HTTP_200_OK)

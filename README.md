# 🌾 VaaniKart – WhatsApp Bot + Web Shopping App for Farmers & Merchants

VaaniKart is a full-stack solution built to empower **farmers and local merchants** by providing:

- 🤖 A **WhatsApp bot** interface (built with Django + Meta API)
- 🛒 A responsive **shopping website** built with **Next.js + TypeScript**
- 🔁 Seamless backend integration via **REST APIs**
- 🧠 Audio-to-text transcription using **Lemonfox API**
- 🗃️ Admin-driven product management

> 🌟 Designed for low-tech users who can interact over WhatsApp, and also for modern users who prefer a UI-based shopping portal.

---

## 🔗 Live Demo

- **Frontend** (Vercel): [https://vaanikart.vercel.app](https://vaanikart.vercel.app)  
- **Backend API** (Render/Railway): `https://<your-backend-url>.com/api/products/`  
- **WhatsApp Bot**: Send a message to: `+91-XXXXXXXXXX`

---

## 🧩 Key Features

| Feature                       | WhatsApp Bot         | Web App                |
|------------------------------|----------------------|------------------------|
| View Products                | ✅ Text & Voice input| ✅ Full catalog view   |
| Voice Message Transcription  | ✅ via Lemonfox API   | ❌                    |
| Admin Product Control        | ✅ (via Django Admin) | ✅                    |
| Category Browsing            | ✅ Text-based         | ✅ Grid/List view     |
| Designed For                 | Farmers / Merchants   | General Users          |

---

## 🛠️ Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Frontend   | Next.js 14 (TypeScript + App Router) |
| Backend    | Django + Django REST Framework       |
| API        | WhatsApp Cloud API + Lemonfox        |
| DB         | SQLite (Dev) / PostgreSQL (Prod)     |
| Deploy     | Vercel (frontend)                    |
| Auth       | Webhook Token Verification           |

---

## 🧠 Architecture

```

User (Farmer) 👩‍🌾       User (Shopper) 🧑‍💻
\|                        |
WhatsApp Message        Web Browser
\|                        |
Meta API               Next.js UI
\|                        |
Django Webhook API <--> REST API (/api/products/)
|
Lemonfox AI (Audio→Text)
|
PostgreSQL DB

````

---

## 🔧 Setup Instructions

### 🐍 Django Backend

#### ✅ Install & Run

```bash
git clone https://github.com/tharun977/VaaniKart.git
cd VaaniKart/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
````

#### 📦 Backend Folder Structure

```
vaanikart/
├── models.py         # Product model
├── views.py          # WhatsApp Webhook + APIView
├── serializers.py    # Product Serializer
├── urls.py           # Product API routes
```

#### 📲 WhatsApp Webhook View (Excerpt)

```python
@csrf_exempt
def whatsapp_webhook(request):
    # Verifies token, listens to messages
    # Replies with uppercase text OR audio transcription
```

---

### 🌐 Next.js Frontend (with TypeScript)

#### ✅ Install & Run

```bash
cd frontend
npm install
npm run dev
```

#### 🌎 Environment Config (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Or for production:

```env
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

#### 🧱 Sample Product Interface

```ts
interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  is_available: boolean;
}
```

#### 🔁 API Fetch (page.tsx)

```ts
const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/products/`)
const products = await res.json()
```

---

## 📦 Product Model

```python
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES)
    price = models.DecimalField(...)
    current_stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
```

---

## 🤖 WhatsApp Bot Setup

### ✅ Meta Developer Setup

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Set up **WhatsApp Cloud API**
3. Create webhook URL: `https://<your-backend>/webhook/`
4. Use the `META_TOKEN`, `VERIFY_TOKEN`, and `META_PHONE_NUMBER_ID` from Meta dashboard

### ✅ Environment Variables (`.env`)

```env
META_TOKEN=your_whatsapp_token
VERIFY_TOKEN=vaanikart_hackathon
LEMONFOX_KEY=your_lemonfox_key
META_PHONE_NUMBER_ID=whatsapp_number_id
```

---

## 🚀 Deployment

### Frontend (Vercel)

* Connect `frontend` directory to Vercel
* Set env var: `NEXT_PUBLIC_API_URL=https://your-django-api-url`


```python
CORS_ALLOWED_ORIGINS = [
    "https://vaanikart.vercel.app"
]
```

---

## 💬 Sample Conversations

🧑 User (Text):

> Show me spices

🤖 Bot:

> SPICES:
>
> * Turmeric Powder – ₹100/kg
> * Chilli Powder – ₹120/kg

🧑 User (Voice):

> *sends voice saying “vegetables”*

🤖 Bot:

> VEGETABLES:
>
> * Tomato – ₹30/kg
> * Onion – ₹25/kg

---

## 🧪 API Testing

* Visit: `http://localhost:8000/api/products/`
* Try in browser or Postman

---

## ❤️ Support This Project

If you like this project, star ⭐ the repo, share it with friends, and contribute!

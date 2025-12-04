# 🍽️ Restaurant Ordering System (Django REST API)

A scalable backend API for managing restaurant orders, menu groups, categories, items, and payments.  
Includes **centralized response formatting, caching, logging, and modular serializers**.

---

## 🚀 Features

- Menu Group, Category & Item CRUD
- Order & Order Items management
- Payment tracking per order
- Response Standardization (Success/Error format)
- Built-in caching (Order detail + Menu items list)
- Logging system with rotating log files
- Extensible clean architecture

---

## 🏗️ Tech Stack

| Component | Technology |
|----------|------------|
| Backend API | Django REST Framework |
| Caching | Django Cache (memory by default, Redis recommended) |
| Database | SQLite (local), PostgreSQL (recommended) |
| Logging | Python `logging` + rotating file handlers |
| Serialization | DRF Model Serializers |
| Architecture | REST, Clean modular design |

---

## 📁 Project Structure

project_root/
│── api/
│ ├── models.py
│ ├── serializers.py
│ ├── views.py
│ ├── urls.py
│── logs/
│ └── api.log
│── manage.py
│── requirements.txt
│── README.md

yaml
Copy code

---

## ⚙️ Installation

### **1️⃣ Clone the repository**
```sh
git clone https://github.com/your-repo/restaurant-api.git
cd restaurant-api
2️⃣ Create Virtual Environment
sh
Copy code
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
3️⃣ Install Dependencies
sh
Copy code
pip install -r requirements.txt
4️⃣ Run Migrations
sh
Copy code
python manage.py makemigrations
python manage.py migrate
5️⃣ Start the Server
sh
Copy code
python manage.py runserver
🔐 Environment Variables
Create a .env file (optional but recommended):

ini
Copy code
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
CACHE_TIMEOUT=60
🧪 Testing the API (Sample CURL Commands)
🛒 Create an Order
sh
Copy code
curl -X POST http://127.0.0.1:8000/api/orders/ \
-H "Content-Type: application/json" \
-d '{
  "order_date": "2025-12-31",
  "status": "completed",
  "items": [
    {
      "item_id": 1,
      "size": "Small",
      "quantity": 2
    }
  ]
}'
💰 Add Payment to an Order
sh
Copy code
curl -X POST http://127.0.0.1:8000/api/orders/1/payments/ \
-H "Content-Type: application/json" \
-d '{
  "method": "card",
  "status": "completed",
  "amount_due": 20.00,
  "total_paid": 20.00
}'
🧰 API Endpoints Overview
Resource	Method	Endpoint
Menu Groups	GET/POST	/api/menu-groups/
Menu Group Detail	GET/PUT/DELETE	/api/menu-groups/{id}/
Categories	GET/POST	/api/categories/
Items	GET/POST	/api/items/
Order List/Create	GET/POST	/api/orders/
Order Detail	GET/PUT/DELETE	/api/orders/{id}/
Payments	GET/POST	/api/payments/
Payments for Order	GET/POST	/api/orders/{order_id}/payments/

⚡ Caching
Endpoint	Cache	Expiry
GET /orders/{id}	Yes	60 sec
GET /items	Yes	5 min
Others	No	—

Redis can be enabled by modifying settings.py.

📝 Logging
Logs stored in:

bash
Copy code
/logs/api.log
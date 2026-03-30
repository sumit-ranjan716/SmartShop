# 🛒 SmartShop — Smart E-Commerce Web Application

A full-featured e-commerce web application built with **Django** and **Bootstrap 5**, featuring an AI-powered **recommendation system** that suggests products based on category, purchase history, and popularity.

---

## ✨ Features

### Core
- **User Authentication** — Register, login, logout, profile management
- **Product Catalog** — Browse, search, filter by category, sort by price/rating/newest
- **Shopping Cart** — Add, update quantity, remove items (works for guests too)
- **Order System** — Full checkout with shipping details, order history, email confirmation
- **Recommendation Engine** — Category-based, "people also bought", popular products

### Advanced
- **Wishlist** — Save products for later
- **Reviews & Ratings** — Rate products 1–5 stars with comments
- **Razorpay Integration** — Test payment gateway support
- **Responsive UI** — Works beautifully on mobile, tablet, and desktop

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+, Django 4.2 |
| Frontend | HTML5, CSS3, Bootstrap 5, Vanilla JS |
| Database | SQLite (default), PostgreSQL-ready |
| Icons | Bootstrap Icons |
| Fonts | Google Fonts (Inter) |

---

## 🚀 Setup Instructions

### 1. Clone the repository
```bash
cd ecommerce_project
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser (admin)
```bash
python manage.py createsuperuser
```
Use `admin` / `admin123` or any credentials you prefer.

### 6. Load sample data
```bash
python manage.py seed_data
```
This creates:
- 6 categories
- 25 products
- 3 test users (`alice`, `bob`, `charlie` — password: `testpass123`)
- Sample reviews and orders

### 7. Run the development server
```bash
python manage.py runserver
```

### 8. Open in browser
- **Home:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/

---

## 📁 Project Structure

```
ecommerce_project/
├── manage.py
├── requirements.txt
├── ecommerce_project/
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Root URL routing
│   └── wsgi.py
├── apps/
│   ├── users/               # Auth, profiles, signals
│   ├── products/             # Products, categories, reviews, wishlist
│   ├── cart/                 # Shopping cart with session support
│   ├── orders/               # Checkout, order management
│   └── recommendations/      # Recommendation engine
├── templates/
│   ├── base.html             # Master template with navbar & footer
│   ├── home.html             # Landing page
│   ├── products/             # Product list, detail, wishlist
│   ├── cart/                 # Cart page
│   ├── orders/               # Checkout, order history/detail
│   └── users/                # Login, register, profile
├── static/
│   ├── css/style.css         # Custom styles
│   ├── js/main.js            # UI interactions
│   └── images/
└── media/
    └── product_images/       # Uploaded product images
```

---

## 🔑 Recommendation System

| Strategy | How It Works |
|----------|-------------|
| **Category-based** | Shows products from the same category |
| **Popular** | Ranks products by total purchase count |
| **Collaborative** | Finds products frequently bought together in past orders |
| **Personalized** | Recommends from categories the user buys from most |

---

## 🎨 UI Highlights

- Glassmorphism navbar with blur effect
- Gradient hero section with floating animation
- Product cards with hover lift effect
- Star rating display
- Auto-dismissing alert notifications
- Back-to-top floating button
- Dark footer with newsletter signup

---

## 📄 License

This project is for educational and portfolio purposes. Feel free to use and modify.

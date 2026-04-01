"""
Management command to populate the database with sample data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.products.models import Category, Product, Review, Brand
from apps.orders.models import Order, OrderItem
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds the database with sample categories, products, users, reviews, and orders.'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database...\n')

        # ---- Brands ----
        brand_data = [
            ('Apple', 'apple', 'Premium electronics and devices', 'USA', True),
            ('Samsung', 'samsung', 'Global leader in electronics and appliances', 'South Korea', True),
            ('Nike', 'nike', 'Sportswear and athletic gear', 'USA', True),
            ('Adidas', 'adidas', 'Sportswear and shoes', 'Germany', True),
            ('Prestige', 'prestige', 'Home and kitchen appliances brand', 'India', False),
            ('Penguin Books', 'penguin-books', 'Publisher of books across genres', 'UK', True),
        ]

        brands = {}
        for name, slug, desc, country, verified in brand_data:
            brand, created = Brand.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': desc,
                    'country_of_origin': country,
                    'is_verified': verified,
                    'is_active': True,
                },
            )
            brands[slug] = brand
            status = '✅ Created' if created else '⏭️ Exists'
            self.stdout.write(f'  {status}: Brand "{name}"')

        # ---- Categories ----
        category_data = [
            ('Electronics', 'electronics', 'Smartphones, laptops, and gadgets'),
            ('Fashion', 'fashion', 'Clothing, shoes, and accessories'),
            ('Home & Kitchen', 'home-kitchen', 'Furniture, appliances, and decor'),
            ('Books', 'books', 'Fiction, non-fiction, and textbooks'),
            ('Sports & Fitness', 'sports-fitness', 'Gym equipment, sportswear, and outdoor gear'),
            ('Beauty & Health', 'beauty-health', 'Skincare, makeup, and wellness products'),
        ]

        categories = {}
        for name, slug, desc in category_data:
            cat, created = Category.objects.get_or_create(
                slug=slug, defaults={'name': name, 'description': desc}
            )
            categories[slug] = cat
            status = '✅ Created' if created else '⏭️ Exists'
            self.stdout.write(f'  {status}: Category "{name}"')

        # ---- Products ----
        products_data = [
            # Electronics
            ('Wireless Bluetooth Headphones', 'wireless-bluetooth-headphones', 'Premium noise-cancelling headphones with 30-hour battery life. Deep bass, clear highs, and ultra-comfortable ear cushions.', 2499.00, 'electronics', 50, True),
            ('Smart Watch Pro', 'smart-watch-pro', 'Advanced fitness tracker with heart rate monitor, GPS, sleep tracking, and 7-day battery. Water resistant to 50m.', 4999.00, 'electronics', 30, True),
            ('USB-C Laptop Charger 65W', 'usb-c-laptop-charger', 'Universal fast charger compatible with all USB-C laptops. GaN technology for compact size and cool operation.', 1299.00, 'electronics', 100, False),
            ('Portable Bluetooth Speaker', 'portable-bluetooth-speaker', 'Waterproof speaker with 360° surround sound. 12-hour playtime, built-in microphone for calls.', 1899.00, 'electronics', 45, False),
            ('Wireless Mouse & Keyboard Combo', 'wireless-mouse-keyboard', 'Ergonomic design with silent keys and precision mouse. USB receiver with 10m range.', 999.00, 'electronics', 80, False),
            ('Power Bank 20000mAh', 'power-bank-20000', 'Fast charging power bank with dual USB-A and USB-C ports. LED display shows remaining charge.', 1499.00, 'electronics', 60, True),

            # Fashion
            ('Classic Denim Jacket', 'classic-denim-jacket', 'Timeless denim jacket in classic blue wash. Premium cotton with brass buttons. Comfortable fit.', 2199.00, 'fashion', 25, True),
            ('Running Shoes Ultra', 'running-shoes-ultra', 'Lightweight running shoes with responsive cushioning and breathable mesh upper. Great for daily runs.', 3499.00, 'fashion', 40, True),
            ('Cotton Polo T-Shirt', 'cotton-polo-tshirt', '100% premium cotton polo. Available in multiple colours. Perfect for casual and semi-formal occasions.', 799.00, 'fashion', 100, False),
            ('Leather Wallet', 'leather-wallet', 'Genuine leather bi-fold wallet with RFID protection. Multiple card slots and coin pocket.', 599.00, 'fashion', 75, False),
            ('Aviator Sunglasses', 'aviator-sunglasses', 'UV400 protection aviator sunglasses with polarized lenses. Lightweight metal frame.', 1299.00, 'fashion', 55, False),

            # Home & Kitchen
            ('Stainless Steel Water Bottle', 'stainless-steel-bottle', 'Double-walled vacuum insulated bottle. Keeps drinks cold 24h or hot 12h. BPA-free, 750ml.', 699.00, 'home-kitchen', 90, False),
            ('Non-Stick Cookware Set', 'non-stick-cookware-set', '5-piece cookware set with granite coating. Includes frying pan, saucepan, kadai, tawa, and spatula.', 2999.00, 'home-kitchen', 20, True),
            ('Automatic Coffee Maker', 'automatic-coffee-maker', 'Programmable coffee maker with built-in grinder. Brews up to 10 cups. Timer and keep-warm function.', 4499.00, 'home-kitchen', 15, True),
            ('LED Desk Lamp', 'led-desk-lamp', 'Adjustable LED desk lamp with 5 brightness levels and 3 colour temperatures. USB charging port.', 1199.00, 'home-kitchen', 35, False),

            # Books
            ('Python Programming Mastery', 'python-programming-mastery', 'Comprehensive guide to Python programming from basics to advanced. 500+ exercises and projects.', 499.00, 'books', 200, True),
            ('The Art of Clean Code', 'art-of-clean-code', 'Learn to write maintainable, scalable code. Best practices, patterns, and real-world examples.', 399.00, 'books', 150, False),
            ('Data Science Handbook', 'data-science-handbook', 'Complete reference for data science with Python. Covers NumPy, Pandas, Scikit-learn, and TensorFlow.', 599.00, 'books', 100, False),
            ('Web Development with Django', 'web-dev-django', 'Build production-grade web applications with Django. From setup to deployment, complete guide.', 549.00, 'books', 80, True),

            # Sports & Fitness
            ('Yoga Mat Premium', 'yoga-mat-premium', 'Extra thick 6mm yoga mat with alignment lines. Non-slip, eco-friendly material. Includes carry strap.', 899.00, 'sports-fitness', 60, False),
            ('Resistance Bands Set', 'resistance-bands-set', 'Set of 5 resistance bands with different tension levels. Includes door anchor, handles, and ankle straps.', 699.00, 'sports-fitness', 45, True),
            ('Adjustable Dumbbells', 'adjustable-dumbbells', 'Space-saving adjustable dumbbells from 2.5kg to 24kg. Quick-change mechanism for seamless workouts.', 6999.00, 'sports-fitness', 10, True),

            # Beauty & Health
            ('Vitamin C Face Serum', 'vitamin-c-serum', 'Brightening face serum with 20% Vitamin C, Hyaluronic Acid, and Vitamin E. For all skin types.', 499.00, 'beauty-health', 70, True),
            ('Natural Hair Oil', 'natural-hair-oil', 'Cold-pressed blend of coconut, argan, and jojoba oils. Strengthens hair, reduces breakage.', 349.00, 'beauty-health', 85, False),
            ('Electric Toothbrush', 'electric-toothbrush', 'Sonic electric toothbrush with 5 cleaning modes. 2-minute smart timer. USB rechargeable.', 1999.00, 'beauty-health', 30, False),
        ]

        products = []
        for name, slug, desc, price, cat_slug, stock, featured in products_data:
            prod, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': desc,
                    'price': Decimal(str(price)),
                    'category': categories[cat_slug],
                    'stock': stock,
                    'featured': featured,
                    'is_active': True,
                }
            )
            # Simple brand assignment by category
            if cat_slug == 'electronics':
                prod.brand = brands.get('apple')
            elif cat_slug == 'fashion':
                prod.brand = brands.get('nike')
            elif cat_slug == 'home-kitchen':
                prod.brand = brands.get('prestige')
            elif cat_slug == 'books':
                prod.brand = brands.get('penguin-books')
            elif cat_slug == 'sports-fitness':
                prod.brand = brands.get('adidas')
            elif cat_slug == 'beauty-health':
                prod.brand = brands.get('nike')
            prod.save()

            products.append(prod)
            status = '✅ Created' if created else '⏭️ Exists'
            self.stdout.write(f'  {status}: Product "{name}"')

        # ---- Sample Users ----
        usernames = ['alice', 'bob', 'charlie']
        users = []
        for uname in usernames:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={'email': f'{uname}@example.com', 'first_name': uname.capitalize()}
            )
            if created:
                user.set_password('testpass123')
                user.save()
            users.append(user)
            status = '✅ Created' if created else '⏭️ Exists'
            self.stdout.write(f'  {status}: User "{uname}"')

        # ---- Sample Reviews ----
        review_comments = [
            'Excellent product! Highly recommended.',
            'Good quality for the price. Happy with my purchase.',
            'Decent product but could be better.',
            'Amazing! Exceeded my expectations.',
            'Very useful. Will buy again.',
            'Great value for money!',
        ]

        review_count = 0
        for user in users:
            # Each user reviews 5 random products
            reviewed = random.sample(products, min(5, len(products)))
            for prod in reviewed:
                _, created = Review.objects.get_or_create(
                    user=user,
                    product=prod,
                    defaults={
                        'rating': random.randint(3, 5),
                        'comment': random.choice(review_comments),
                    }
                )
                if created:
                    review_count += 1

        self.stdout.write(f'  ✅ Created {review_count} reviews')

        # ---- Sample Orders ----
        order_count = 0
        for user in users:
            for _ in range(2):
                order = Order.objects.create(
                    user=user,
                    full_name=user.first_name or user.username,
                    email=user.email,
                    phone='9876543210',
                    address='123 Main Street',
                    city='Mumbai',
                    state='Maharashtra',
                    zipcode='400001',
                    payment_method='cod',
                    status=random.choice(['completed', 'pending', 'delivered']),
                )
                # Add 2-4 random items to each order
                order_products = random.sample(products, random.randint(2, 4))
                total = Decimal('0')
                for prod in order_products:
                    qty = random.randint(1, 3)
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        product_name=prod.name,
                        price=prod.price,
                        quantity=qty,
                    )
                    total += prod.price * qty
                order.subtotal = total
                order.total = total
                order.save()
                order_count += 1

        self.stdout.write(f'  ✅ Created {order_count} orders')

        self.stdout.write(self.style.SUCCESS('\n🎉 Database seeded successfully!'))
        self.stdout.write(f'   📦 {Product.objects.count()} products')
        self.stdout.write(f'   📁 {Category.objects.count()} categories')
        self.stdout.write(f'   👤 {User.objects.count()} users')
        self.stdout.write(f'   ⭐ {Review.objects.count()} reviews')
        self.stdout.write(f'   🛒 {Order.objects.count()} orders')
        self.stdout.write(f'\n   Admin: username=admin, password=admin123')
        self.stdout.write(f'   Test users: alice/bob/charlie, password=testpass123')

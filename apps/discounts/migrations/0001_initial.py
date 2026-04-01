from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0002_order_payment_choices_update'),
        ('products', '0002_brand_and_product_brand'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CouponCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=50, unique=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage %'), ('flat', 'Flat Amount ₹')], max_length=20)),
                ('value', models.DecimalField(decimal_places=2, max_digits=6)),
                ('min_order_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('max_discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('applies_to', models.CharField(choices=[('all', 'All Products'), ('category', 'Specific Category'), ('product', 'Specific Product'), ('seller', 'Seller Products')], default='all', max_length=20)),
                ('usage_limit', models.PositiveIntegerField(default=100)),
                ('usage_per_user', models.PositiveIntegerField(default=1)),
                ('times_used', models.PositiveIntegerField(default=0)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.category')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-id']},
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage %'), ('flat', 'Flat Amount ₹')], max_length=20)),
                ('value', models.DecimalField(decimal_places=2, max_digits=6)),
                ('max_discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('label', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.category')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discounts', to='products.product')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='CouponUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used_at', models.DateTimeField(auto_now_add=True)),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usages', to='discounts.couponcode')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-used_at']},
        ),
    ]


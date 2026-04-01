from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('orders', '0003_order_discount_tracking_and_coupon'),
        ('products', '0002_brand_and_product_brand'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RefundPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('photo', models.ImageField(upload_to='refund_photos/%Y/%m/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='RefundRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('defective', 'Defective/Damaged'), ('wrong_item', 'Wrong Item Received'), ('not_as_described', 'Not as Described'), ('changed_mind', 'Changed Mind'), ('other', 'Other')], max_length=50)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('seller_review', 'Seller Reviewing'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('completed', 'Completed')], default='pending', max_length=30)),
                ('seller_note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.orderitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ExchangeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('defective', 'Defective/Damaged'), ('wrong_item', 'Wrong Item Received'), ('not_as_described', 'Not as Described'), ('changed_mind', 'Changed Mind'), ('other', 'Other')], max_length=50)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('seller_review', 'Seller Reviewing'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('completed', 'Completed')], default='pending', max_length=30)),
                ('seller_note', models.TextField(blank=True)),
                ('exchange_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('exchange_for_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.orderitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]


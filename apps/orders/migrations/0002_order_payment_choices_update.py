from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('cod', 'Cash on Delivery'),
                    ('stripe', 'Credit/Debit Card (Stripe)'),
                    ('upi', 'UPI / QR Code'),
                ],
                default='cod',
                max_length=20,
            ),
        ),
    ]


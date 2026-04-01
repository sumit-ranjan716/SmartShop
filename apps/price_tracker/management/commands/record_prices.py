from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.products.models import Product
from apps.price_tracker.models import ProductPriceHistory, PriceAlert
from apps.price_tracker.email_utils import send_price_drop_alert


class Command(BaseCommand):
    help = 'Records current prices for active products and triggers alerts.'

    def handle(self, *args, **options):
        active_products = Product.objects.filter(is_active=True).iterator()
        prices_recorded = 0
        alerts_triggered = 0

        now = timezone.now()

        for product in active_products:
            current_price = product.price
            
            # Check price history
            last_history = product.price_history.order_by('-recorded_at').first()
            if not last_history or last_history.price != current_price:
                ProductPriceHistory.objects.create(product=product, price=current_price)
                prices_recorded += 1

            # Check price alerts
            active_alerts = PriceAlert.objects.filter(
                product=product,
                is_active=True,
                target_price__gte=current_price
            ).select_related('user')

            if active_alerts.exists():
                for alert in active_alerts:
                    send_price_drop_alert(alert, current_price)
                    alert.is_active = False
                    alert.triggered_at = now
                    alert.save(update_fields=['is_active', 'triggered_at'])
                    alerts_triggered += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully recorded {prices_recorded} price changes and triggered {alerts_triggered} alerts.'
            )
        )

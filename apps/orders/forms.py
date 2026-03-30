"""Forms for the checkout process."""
from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    """Checkout form for shipping details and payment method."""
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'state', 'zipcode', 'payment_method']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'payment_method':
                field.widget.attrs['class'] = 'form-select'
            elif field_name == 'address':
                field.widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
            else:
                field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

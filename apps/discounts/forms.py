from django import forms

from .models import CouponCode, Discount


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = [
            'product', 'category', 'discount_type', 'value', 'max_discount_amount',
            'start_date', 'end_date', 'is_active', 'label',
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('product') and not cleaned.get('category'):
            raise forms.ValidationError('Select either a product or a category for discount.')
        if cleaned.get('product') and cleaned.get('category'):
            raise forms.ValidationError('Choose product OR category, not both.')
        if cleaned.get('start_date') and cleaned.get('end_date') and cleaned['start_date'] >= cleaned['end_date']:
            raise forms.ValidationError('End date must be after start date.')
        return cleaned


class CouponCodeForm(forms.ModelForm):
    class Meta:
        model = CouponCode
        fields = [
            'code', 'discount_type', 'value', 'min_order_amount', 'max_discount_amount',
            'applies_to', 'product', 'category', 'usage_limit', 'usage_per_user',
            'start_date', 'end_date', 'is_active',
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SAVE20'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_order_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'applies_to': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'usage_per_user': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        applies_to = cleaned.get('applies_to')
        if applies_to == 'product' and not cleaned.get('product'):
            raise forms.ValidationError('Select a product for product-specific coupon.')
        if applies_to == 'category' and not cleaned.get('category'):
            raise forms.ValidationError('Select a category for category-specific coupon.')
        if cleaned.get('start_date') and cleaned.get('end_date') and cleaned['start_date'] >= cleaned['end_date']:
            raise forms.ValidationError('End date must be after start date.')
        return cleaned


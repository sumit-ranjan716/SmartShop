from django import forms
from django.forms import modelformset_factory
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import OrderItem

from .models import ExchangeRequest, RefundPhoto, RefundRequest


class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['order_item', 'reason', 'description']
        widgets = {
            'order_item': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)
        qs = OrderItem.objects.none()
        if user and order:
            qs = OrderItem.objects.filter(order=order, order__user=user)
        self.fields['order_item'].queryset = qs

    def clean_order_item(self):
        item = self.cleaned_data['order_item']
        if item.order.status not in ['delivered', 'completed']:
            raise forms.ValidationError('Refund is allowed only for delivered/completed orders.')
        if timezone.now() > item.order.created_at + timedelta(days=7):
            raise forms.ValidationError('Refund window (7 days) has expired.')
        return item


class ExchangeRequestForm(forms.ModelForm):
    class Meta:
        model = ExchangeRequest
        fields = ['order_item', 'reason', 'description', 'exchange_for_product', 'exchange_notes']
        widgets = {
            'order_item': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'exchange_for_product': forms.Select(attrs={'class': 'form-select'}),
            'exchange_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)
        qs = OrderItem.objects.none()
        if user and order:
            qs = OrderItem.objects.filter(order=order, order__user=user)
        self.fields['order_item'].queryset = qs


class RefundPhotoForm(forms.ModelForm):
    class Meta:
        model = RefundPhoto
        fields = ['photo']
        widgets = {'photo': forms.ClearableFileInput(attrs={'class': 'form-control'})}

    def clean_photo(self):
        p = self.cleaned_data['photo']
        if p and p.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Each photo must be 5MB or smaller.')
        return p


PhotoUploadFormSet = modelformset_factory(
    RefundPhoto,
    form=RefundPhotoForm,
    extra=5,
    max_num=5,
    validate_max=True,
)


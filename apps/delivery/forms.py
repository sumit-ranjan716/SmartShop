"""Forms for the delivery app."""
from django import forms
from .models import DeliveryAssignment


class AssignDeliveryForm(forms.Form):
    """Admin/seller form to assign a delivery person to an order."""
    delivery_person = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Select Delivery Person',
    )

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if queryset is not None:
            self.fields['delivery_person'].queryset = queryset


class UpdateStatusForm(forms.Form):
    """Form for delivery person to update assignment status."""
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional note...'}),
    )


class CancelDeliveryForm(forms.Form):
    """Cancellation form with reason and details."""
    reason = forms.ChoiceField(
        choices=DeliveryAssignment.CANCELLATION_REASONS,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Cancellation Reason',
    )
    details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional details...'}),
    )

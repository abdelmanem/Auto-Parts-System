from django import forms
from .models import Part, Category, Manufacturer, CarModel, Supplier

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = [
            'name',
            'part_number',
            'category',
            'manufacturer',
            'compatible_cars',
            'description',
            'condition',
            'price',
            'purchase_price',
            'stock_quantity',
            'min_stock_level',
            'location',
            'weight',
            'dimensions',
            'image',
            'is_active'
        ]
        widgets = {
            'compatible_cars': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name',
            'tax_number',
            'contact_person',
            'email',
            'phone',
            'address',
            'website',
            'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
        if not forms.EmailField().clean(email):
            raise forms.ValidationError('يرجى إدخال عنوان بريد إلكتروني صحيح')
        return email
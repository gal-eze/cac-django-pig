from datetime import date

from django import forms
from django.db.models import Q

from .models import Security, Transaction


class UploadFileForm(forms.Form):
    securities_csv_file = forms.FileField(label="Archivo de Valores Negocialbes (CSV)")

    def clean_csv_file(self):
        csv_file = self.cleaned_data["securities_csv_file"]
        # Verificar que el archivo tenga la extensión .csv
        if not csv_file.name.endswith(".csv"):
            raise forms.ValidationError("El archivo debe tener extensión .csv")
        return csv_file


class TransactionForm(forms.ModelForm):
    symbol = forms.CharField(
        label="Ticker",
        max_length=5,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    def clean_symbol(self):
        symbol = self.cleaned_data["symbol"]
        try:
            security = Security.objects.get(Q(symbol__iexact=symbol))
        except Security.DoesNotExist:
            raise forms.ValidationError("El ticker ingresado no existe.")
        return security

    def clean_date(self):
        cleaned_date = self.cleaned_data["date"]

        if cleaned_date > date.today():
            raise forms.ValidationError(
                "La fecha no puede ser mayor a la fecha actual."
            )

        return cleaned_date

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.security = self.cleaned_data["symbol"]

        if commit:
            transaction.save()

        return transaction

    class Meta:
        model = Transaction
        fields = ["symbol", "date", "quantity", "price", "broker"]
        widgets = {
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "broker": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {"price": "Precio", "quantity": "Cantidad"}

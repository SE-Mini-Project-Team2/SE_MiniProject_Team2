from django import forms

from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "price", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"maxlength": 255}),
            "author": forms.TextInput(attrs={"maxlength": 255}),
            "price": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Title is required.")
        return title

    def clean_author(self):
        author = self.cleaned_data["author"].strip()
        if not author:
            raise forms.ValidationError("Author is required.")
        return author
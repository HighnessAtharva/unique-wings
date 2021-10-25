from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    """Creates Contact form"""

    class Meta:
        model = Contact
        fields = (
            'full_name',
            'email',
            'subject',
            'message',
            )

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Your Full Name...',
            'email': 'Your Email Address...',
            'subject': 'Subject',
            'message': 'Message Here...',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True

        for field in self.fields:
            print(field)
            if field != 'subject':
                placeholder = f'{placeholders[field]} *'
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False
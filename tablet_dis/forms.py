from django import forms
from django.utils.translation import gettext_lazy as _

class TabletSearchForm(forms.Form):
    query = forms.CharField(
        label=_('Search Tablet'),
        max_length=100,
        min_length=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg input-zen w-100',
            'placeholder': _('Enter Medicine name ( Tablets , Ointments )'),
            'autocomplete': 'off',
            'id': 'tablet-search-input'
        }),
        error_messages={
            'required': _('Please enter a tablet name to search.'),
            'min_length': _('Please enter at least 2 characters.')
        }
    )

    def clean_query(self):
        query = self.cleaned_data.get('query', '').strip()
        if not query:
            raise forms.ValidationError(_('Please enter a tablet name.'))
        return query.title()  # Capitalize first letter of each word
from django import forms
from django.utils.translation import gettext_lazy as _

from tablet_dis.tablet_checker import validate_input_format


class TabletSearchForm(forms.Form):
    name = forms.CharField(
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

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        result = validate_input_format(name)
        if not result.ok:
            raise forms.ValidationError(_('Invalid input'))
        return result.normalized
from django import forms
from vocabularies.models import Vocabulary, Word


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['word']

    def clean(self):
        cleaned_data = super(WordForm, self).clean()
        return cleaned_data


class ButtonDeleteForm(forms.Form):
    button_clicked = forms.CharField(widget=forms.HiddenInput())


class ButtonDeleteAllForm(forms.Form):
    delete_all_history = forms.CharField(widget=forms.HiddenInput(), required=False)

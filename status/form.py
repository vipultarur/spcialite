from django import forms
from .models import Status
from .models import Highlight, Status

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['media', 'caption']

    def clean_media(self):
        media = self.cleaned_data.get('media')
        if media:
            # File size limit can also be set here (optional)
            if media.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("File is too large. Max size is 10MB.")
        return media
    
class HighlightCreateForm(forms.ModelForm):
    statuses = forms.ModelMultipleChoiceField(
        queryset=Status.objects.none(),  # Dynamically populated later
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    
    class Meta:
        model = Highlight
        fields = ['title', 'cover', 'statuses']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pass user to limit statuses
        super().__init__(*args, **kwargs)
        if user:
            self.fields['statuses'].queryset = Status.objects.filter(user=user)  
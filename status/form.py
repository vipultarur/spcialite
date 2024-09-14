from django import forms
from .models import Status

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
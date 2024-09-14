from django import forms
from post.models import Post,Reel


class NewPostform(forms.ModelForm):
    
    picture = forms.ImageField(required=False)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=True)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Seperate with comma'}), required=True)

    class Meta:
        model = Post
        fields = ['picture',  'caption', 'tags']

class NewReelForm(forms.ModelForm):
    video = forms.FileField(required=True)
    thumbnail=forms.ImageField(required=False)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=True)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Separate with comma'}), required=True)

    class Meta:
        model = Reel
        fields = ['video', 'caption', 'tags','thumbnail']

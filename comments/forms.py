from django.contrib.auth.models import User
from comments.models import Comments, ReelComment
from django import forms

class CommentForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w-full resize-none !bg-transparent px-4 py-2 focus:!border-transparent focus:!ring-transparent',
                'placeholder': 'Write comment'
            }
        ),
        required=True
    )
    
    class Meta:
        model = Comments
        fields = ('body',)

class ReelCommentForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'w-full resize-none !bg-transparent px-4 py-2 focus:!border-transparent focus:!ring-transparent',
                'placeholder': 'Write a comment'
            }
        ),
        required=True
    )

    class Meta:
        model = ReelComment
        fields = ('body',)

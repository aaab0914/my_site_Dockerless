from django import forms

from .models import Comment, Post
from taggit.forms import TagWidget


class EmailPostForm(forms.Form):
    name = forms.CharField(
        max_length=25,
        min_length=2,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    to = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
    )

    # def clean_name(self):
    #     name = self.cleaned_data['name']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body", "image"]
        widgets = {
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }
        labels = {
            'body': 'Your comment',
            'image': 'Attach an image {optional}',
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        min_length=1,
        max_length=200,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Search Posts here...'}
        ),
    )


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "tags", "cover_image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
            "tags": forms.TextInput(attrs={"class": "form-control"}),
            "cover_image": forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Post title',
            'body': 'Post content',
            'tags': 'Tags (comma separated)',
            'cover_image': 'Cover image (optional)',
        }

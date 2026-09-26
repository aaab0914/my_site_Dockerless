from django import forms

from .models import Comment, Post


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comment = forms.CharField(required=False, widget=forms.Textarea)

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


class SearchForm(forms.Form):
    query = forms.CharField()


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "tags", "cover_image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
            "tags": forms.TextInput(attrs={"class": "form-control"}),
            "cover_image": forms.FileInput(attrs={"class": "form-control"}),
        }

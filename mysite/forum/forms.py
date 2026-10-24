from django import forms
from .models import Topic, Reply

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'content']

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3})
        }

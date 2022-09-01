from django.forms import ModelForm

from .models import Comment, Post, Reply


class CreatePostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('content', 'attachment',)


class CreateCommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('content',)


class CreateReplyForm(ModelForm):

    class Meta:
        model = Reply
        fields = ('content',)

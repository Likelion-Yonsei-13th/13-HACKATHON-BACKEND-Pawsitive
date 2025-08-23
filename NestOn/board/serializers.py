from rest_framework import serializers
from .models import Post, Comment, Like, Report

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    is_mine = serializers.SerializerMethodField()
    post_id = serializers.IntegerField(source='post.id', read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_category_display = serializers.CharField(source='post.get_category_display', read_only=True)


    class Meta:
        model = Comment
        fields = ['id', 'author_username', 'content', 'created_at', 'updated_at', 'is_mine', 'post_id', 'post_title', 'post_category_display']

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.author == request.user
        return False

class PostListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'author_username', 'created_at', 'view_count', 
                  'comment_count', 'like_count', 'category', 'category_display']

class PostDetailSerializer(PostListSerializer):
    comments = CommentSerializer(source='comments.filter(is_active=True)', many=True, read_only=True)
    is_mine = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['content', 'updated_at', 'comments', 'is_mine', 'is_liked']
    
    def get_is_mine(self, obj):
        return obj.author == self.context['request'].user
    
    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Like.objects.filter(post=obj, user=user).exists()
        return False

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category']

class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reason']
from rest_framework import serializers
from .models import Post, Comment

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    is_mine = serializers.SerializerMethodField()
    # 댓글이 속한 게시글의 id와 title을 추가
    post_id = serializers.IntegerField(source='post.id', read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = Comment
        # fields에 post_id와 post_title 추가
        fields = ['id', 'author_username', 'content', 'created_at', 'updated_at', 'is_mine', 'post_id', 'post_title']

    def get_is_mine(self, obj):
        # self.context에 'request'가 없는 경우를 대비
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.author == request.user
        return False

class PostListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'author_username', 'created_at', 'view_count', 'comment_count', 'like_count']

class PostDetailSerializer(PostListSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    # 현재 로그인한 유저가 게시글 작성자인지 여부를 반환
    is_mine = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['content', 'updated_at', 'comments', 'is_mine']
    
    def get_is_mine(self, obj):
        return obj.author == self.context['request'].user
    
    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            # Like 모델에서 현재 유저와 게시글에 해당하는 좋아요 기록이 있는지 확인
            return Like.objects.filter(post=obj, user=user).exists()
        return False

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content']

class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']
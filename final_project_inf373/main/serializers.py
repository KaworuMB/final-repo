from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, Document, Comment, Member, User

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'project', 'name', 'file']

class CommentSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    is_project_owner = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'project', 'user', 'text', 'created_at', 'is_owner', 'is_project_owner', 'username']
        read_only_fields = ['user']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return obj.user == request.user if request else False

    def get_is_project_owner(self, obj):
        request = self.context.get('request')
        return obj.project.owner == request.user if request else False

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'owner', 'documents', 'comments']

class MemberSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='member.id', read_only=True)
    username = serializers.CharField(source='member.username', read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'username', 'is_owner']

    def get_is_owner(self, obj):
        return obj.project.owner_id == obj.member_id
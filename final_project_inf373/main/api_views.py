from rest_framework import viewsets, permissions, status
from .models import Project, Document, Comment, Member, User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.core.mail import send_mail
from rest_framework.decorators import action
from django.http import FileResponse
from .serializers import (
    ProjectSerializer, DocumentSerializer,
    CommentSerializer, MemberSerializer
)
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        user = request.user
        if comment.user == user or comment.project.owner == user:
            return super().destroy(request, *args, **kwargs)
        return Response({'detail': 'Not allowed to delete this comment.'}, status=403)

    @action(detail=False, methods=['get'], url_path='by-project/(?P<project_id>[^/.]+)')
    def by_project(self, request, project_id=None):
        comments = Comment.objects.filter(project_id=project_id)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        comments = Comment.objects.filter(user_id=user_id)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        Member.objects.create(member=self.request.user, project=project, is_owner=True)

        cache_key = f"user-projects:{self.request.user.id}"
        cache.delete(cache_key)

    def get_queryset(self):
        user = self.request.user
        cache_key = f"user-projects:{user.id}"
        cached_projects = cache.get(cache_key)

        if cached_projects is not None:
            return cached_projects

        owned = Project.objects.filter(owner=user)
        member = Project.objects.filter(members__member=user)
        projects = (owned | member).distinct()

        cache.set(cache_key, projects, timeout=300)
        return projects

    @action(detail=True, methods=['get'], url_path='members')
    def project_members(self, request, pk=None):
        project = self.get_object()
        members = Member.objects.filter(project=project)
        serialized_members = MemberSerializer(members, many=True).data

        return Response({
            'members': serialized_members,
            'current_user_id': request.user.id,
            'owner_id': project.owner.id,
        })


class MemberViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        members = Member.objects.filter(project=project)
        serializer = MemberSerializer(members, many=True)
        return Response({
            "members": serializer.data,
            "current_user_id": request.user.id,
            "owner_id": project.owner.id
        })

    def create(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        if request.user != project.owner:
            return Response({'detail': 'Only owner can add members.'}, status=403)

        user_id = request.data.get('member')
        if not user_id:
            return Response({'detail': 'User ID is required.'}, status=400)

        user = get_object_or_404(User, id=user_id)
        member, created = Member.objects.get_or_create(member=user, project=project)
        if not created:
            return Response({'detail': 'Member already exists.'}, status=400)

        serializer = MemberSerializer(member)
        return Response(serializer.data, status=201)

    def destroy(self, request, pk=None, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        member = get_object_or_404(Member, member__id=pk, project=project)

        if request.user != project.owner:
            return Response(
                {'detail': 'Only the project owner can remove members.'},
                status=403
            )

        if member.member == request.user:
            return Response(
                {'detail': 'You cannot remove yourself from the project.'},
                status=403
            )

        member.delete()
        return Response(status=204)

    @action(detail=False, methods=['post'], url_path='invite')
    def invite_member(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)

        if request.user != project.owner:
            return Response({'detail': 'Only owner can invite members.'}, status=403)

        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required.'}, status=400)

        user = User.objects.filter(email=email).first()

        if user:
            member, created = Member.objects.get_or_create(member=user, project=project)
            if not created:
                return Response({'detail': 'User is` already a member of the project.'}, status=400)

            return Response({'detail': f'{email} has been added to the project.'}, status=status.HTTP_200_OK)

        send_mail(
            'Project Invitation',
            f'You have been invited to join the project {project.name}. Click the link to join.',
            'from@example.com',  # Замените на ваш рабочий email
            [email],
            fail_silently=False,
        )

        return Response({'detail': f'Invite sent to {email}.'}, status=status.HTTP_200_OK)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        project_id = self.request.data.get("project")
        project = get_object_or_404(Project, id=project_id)

        if self.request.user != project.owner and not project.members.filter(member=self.request.user).exists():
            raise PermissionDenied("You do not have permission to upload documents for this project.")

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        project = document.project

        if request.user != project.owner and not project.members.filter(member=request.user).exists():
            raise PermissionDenied("You do not have permission to delete this document.")

        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        document = self.get_object()
        file_handle = document.file.open('rb')
        response = FileResponse(file_handle, as_attachment=True, filename=document.file.name.split('/')[-1])
        return response
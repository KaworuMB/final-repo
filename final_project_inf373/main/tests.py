from main.models import Project, Comment, Member
from main.models import User, Project, Member
from main.models import Project, Document, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from main.models import Project
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model


class CommentAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpass')

        self.project = Project.objects.create(project_name='Test Project', owner=self.user1)
        Member.objects.create(member=self.user1, project=self.project, is_owner=True)
        Member.objects.create(member=self.user2, project=self.project)

        self.comment1 = Comment.objects.create(text='User1 Comment', user=self.user1, project=self.project)
        self.comment2 = Comment.objects.create(text='User2 Comment', user=self.user2, project=self.project)

        self.url_list = reverse('comment-list')  # /api/comments/

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_list_comments(self):
        self.authenticate(self.user1)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_comment(self):
        self.authenticate(self.user1)
        data = {'project': self.project.id, 'text': 'New comment'}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)

    def test_delete_own_comment(self):
        self.authenticate(self.user1)
        url = reverse('comment-detail', args=[self.comment1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_owner_can_delete_others_comment(self):
        self.authenticate(self.user1)
        url = reverse('comment-detail', args=[self.comment2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_delete_others_comment(self):
        self.authenticate(self.user2)
        url = reverse('comment-detail', args=[self.comment1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
class DocumentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='user@example.com', password='password')
        self.other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='password')
        self.project = Project.objects.create(project_name='Test Project', owner=self.user)
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_upload_document(self):
        url = reverse('document-list')
        file_data = SimpleUploadedFile("file.txt", b"file_content", content_type="text/plain")
        data = {'project': self.project.id, 'name': 'Doc1', 'file': file_data}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)

    def test_unauthorized_upload(self):
        self.client.credentials()  # Remove auth
        url = reverse('document-list')
        file_data = SimpleUploadedFile("file.txt", b"file_content", content_type="text/plain")
        data = {'project': self.project.id, 'name': 'Doc1', 'file': file_data}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_document_by_owner(self):
        document = Document.objects.create(project=self.project, name='Doc to delete')
        url = reverse('document-detail', args=[document.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Document.objects.count(), 0)

    def test_delete_document_forbidden(self):
        document = Document.objects.create(project=self.project, name='Doc')
        self.client.force_authenticate(user=self.other_user)
        url = reverse('document-detail', args=[document.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
class MemberTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='ownerpass', email='owner@example.com')
        self.user2 = User.objects.create_user(username='user2', password='user2pass', email='user2@example.com')
        self.user3 = User.objects.create_user(username='user3', password='user3pass', email='user3@example.com')

        self.project = Project.objects.create(project_name='Project A', owner=self.owner)
        Member.objects.create(project=self.project, member=self.owner, is_owner=True)

        self.authenticate(self.owner)

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_owner_can_list_members(self):
        url = reverse('project-members-list', args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner_id'], self.owner.id)
        self.assertEqual(len(response.data['members']), 1)

    def test_owner_can_remove_member(self):
        Member.objects.create(project=self.project, member=self.user2)
        url = reverse('project-members-detail', args=[self.project.id, self.user2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Member.objects.filter(project=self.project, member=self.user2).exists())

    def test_owner_cannot_remove_self(self):
        url = reverse('project-members-detail', args=[self.project.id, self.owner.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_cannot_remove_other(self):
        Member.objects.create(project=self.project, member=self.user2)
        self.authenticate(self.user2)
        url = reverse('project-members-detail', args=[self.project.id, self.owner.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_owner_can_invite_existing_user_by_email(self):
        existing_user = User.objects.create_user(username='invited', email='invitee@example.com', password='pass')
        url = reverse('project-members-invite-member', args=[self.project.id])
        response = self.client.post(url, {'email': 'invitee@example.com'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Member.objects.filter(project=self.project, member=existing_user).exists())
        self.assertIn('has been added', response.data['detail'])

    def test_inviting_without_email_returns_400(self):
        url = reverse('project-members-invite-member', args=[self.project.id])
        response = self.client.post(url, {})  # No email
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email is required', response.data['detail'])


class ProjectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='anotheruser', email='another@example.com', password='anotherpass')

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {self.token}'
        }

    def test_create_project(self):
        url = reverse('project-list')
        data = {'project_name': 'Test Project'}
        response = self.client.post(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().project_name, 'Test Project')

    def test_list_projects(self):
        Project.objects.create(project_name='My Project', owner=self.user)
        url = reverse('project-list')
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_only_authenticated_can_create(self):
        url = reverse('project-list')
        response = self.client.post(url, {'project_name': 'Unauthorized'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_project_owner_can_be_fetched(self):
        project = Project.objects.create(project_name='Owned Project', owner=self.user)
        url = reverse('project-detail', args=[project.id])
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner']['username'], self.user.username)

    def test_update_project(self):
        project = Project.objects.create(project_name='Old Name', owner=self.user)
        url = reverse('project-detail', args=[project.id])
        response = self.client.patch(url, {'project_name': 'Updated Name'}, content_type='application/json', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], 'Updated Name')



class UserTests(APITestCase):
    def test_user_registration(self):
        url = '/api/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_missing_fields(self):
        url = '/api/auth/register/'
        response = self.client.post(url, {'username': 'noemail'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_current_user(self):
        # Создаем пользователя
        user = User.objects.create_user(username='me', password='pass123')

        # Получаем токен
        response = self.client.post('/api/auth/login/', {
            'username': 'me',
            'password': 'pass123'
        })
        access_token = response.data['access']

        # Добавляем токен в заголовки
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        # Делаем запрос
        response = self.client.get('/api/auth/current_user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'me')

    def test_get_current_user_unauthenticated(self):
        response = self.client.get('/api/auth/current_user/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class TokenAuthTests(APITestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'strongpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_obtain_token_pair_valid_credentials(self):
        url = '/api/auth/login/'
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_pair_invalid_credentials(self):
        url = '/api/auth/login/'
        data = {
            'username': self.username,
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)






class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.refresh_url = '/api/auth/refresh/'
        self.current_user_url = '/api/auth/current_user/'
        self.logout_url = '/api/auth/logout/'  # если реализовано

        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'strongpassword123'
        }
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )

    def test_user_registration(self):
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        login_response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        refresh_token = login_response.data['refresh']
        refresh_response = self.client.post(self.refresh_url, {
            'refresh': refresh_token
        })
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn('access', refresh_response.data)


    def test_protected_endpoint_with_token(self):
        login_response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user_data['username'])

    def test_protected_endpoint_requires_authentication(self):
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, 401)
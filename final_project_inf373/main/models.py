from django.contrib.auth.models import AbstractUser
from django.db import models
from final_project.storages import MinIOStorage

class User(AbstractUser):
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.username

class Project(models.Model):
    project_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')

    def __str__(self):
        return self.project_name

class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(storage=MinIOStorage(), upload_to='documents/', blank=True, null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Member(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    is_owner = models.BooleanField(default=False)

    class Meta:
        unique_together = ('member', 'project')

    def __str__(self):
        return f"{self.member.username} in {self.project.project_name}"

class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    @property
    def username(self):
        return self.user.username

    @property
    def project_name(self):
        return self.project.project_name
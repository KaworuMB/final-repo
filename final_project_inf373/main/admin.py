from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'owner')
    search_fields = ('project_name',)
    list_filter = ('owner',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'file')
    search_fields = ('name',)
    list_filter = ('project',)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member', 'project')
    list_filter = ('project', 'member')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'username', 'text')
    search_fields = ('username', 'text')
    list_filter = ('project',)


"""
URL configuration for final_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularSwaggerView, SpectacularAPIView
)
from main.views import CurrentUserView, RegisterView
from main.api_views import ProjectViewSet, DocumentViewSet, CommentViewSet, MemberViewSet
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf import settings

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'comments', CommentViewSet)

projects_router = NestedSimpleRouter(router, r'projects', lookup='project')
projects_router.register(r'members', MemberViewSet, basename='project-members')
project_members = MemberViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'delete': 'destroy'
})

urlpatterns = [
    path('silk/', include('silk.urls', namespace='silk')),
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/current_user/', CurrentUserView.as_view(), name='current_user'),
    path('api/', include(router.urls)),
    path('api/', include(projects_router.urls)),
    path('', lambda request: redirect('/login/')),
    # re_path(r'^.*$', FrontendAppView.as_view(), name='frontend'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

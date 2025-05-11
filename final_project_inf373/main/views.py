from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, UserSerializer
from django.views.generic import TemplateView
from django.shortcuts import render

# class FrontendAppView(TemplateView):
#     template_name = "index.html"
#
#     def get(self, request, *args, **kwargs):
#         return render(request, self.template_name)
class RegisterView(APIView):
    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer, 400: RegisterSerializer}
    )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully', 'user': user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer}
    )

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)



from contextlib import contextmanager

from django.contrib.auth import authenticate
from rest_framework import viewsets, status, mixins, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from Backends.models import Topic, User
from Backends.serializer import TopicSerializer, CuttedUserSerializer, CreateUserSerializer


class CreateUserViewSet(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        password = request.data.get('password')
        if password:
            new_user = User.objects.create(**request.data)
            new_user.set_password(password)
            new_user.save()
            return Response(self.serializer_class(new_user).data)
        else:
            return Response("Password not set", status=status.HTTP_400_BAD_REQUEST)


class UserAuthentication(APIView):
    def post(self, request):
        password = request.data.get('password')
        username = request.data.get('username')

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Login failed"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(CuttedUserSerializer(user).data)


class UserViewSet(mixins.RetrieveModelMixin,
                  generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = CuttedUserSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class AllUsersViewSet(mixins.ListModelMixin,
                  generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = CuttedUserSerializer


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def get_queryset(self):
        author = self.request.query_params.get('author', None)
        title = self.request.query_params.get('title', None)
        text = self.request.query_params.get('text', None)
        is_reversed = bool(self.request.query_params.get('reverse', False))

        result_queryset = self.queryset

        if author is not None:
            result_queryset = result_queryset.filter(author=author)

        if title is not None:
            result_queryset = result_queryset.filter(title=title)

        if text is not None:
            result_queryset = result_queryset.filter(text__contains=text)

        if is_reversed:
            result_queryset = result_queryset.order_by('-id')

        return result_queryset

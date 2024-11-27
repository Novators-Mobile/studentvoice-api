from rest_framework.decorators import api_view
from rest_framework.response import Response
from .filters import UniversityFilter, SubjectFilter, MeetingFilter, TeacherFilter

from .serializers import *
from .decorators import admin_required
from rest_framework import status
from .models import CustomUser, University
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import generate_password
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from .authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

login_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['username', 'password'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
    },
)


@swagger_auto_schema(request_body=login_body,
                     methods=['post'],
                     responses={
                         200: 'token',
                         400: 'username and password must be provided',
                         403: 'wrong username or password'
                     })
@api_view(['POST'])
def login(request):
    if 'username' not in request.data or 'password' not in request.data:
        return Response({"detail": "username and password must be provided"}, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(CustomUser, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "wrong username or password"}, status=status.HTTP_403_FORBIDDEN)

    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})


@swagger_auto_schema(methods=['post'],
                     request_body=login_body,
                     responses={
                         200: 'token',
                         400: 'username and password must be provided'
                     })
@api_view(['POST'])
def signup(request):
    if 'username' not in request.data or 'password' not in request.data:
        return Response({"detail": "username and password must be provided"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = CustomUser.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def check_token(request):
    return Response({"passed for {}".format(request.user.username)})


@swagger_auto_schema(method='post', request_body=UniversitySerializer)
@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('search', openapi.IN_QUERY, 'field for search', required=False,
                      type=openapi.TYPE_STRING),
    openapi.Parameter('name', openapi.IN_QUERY, 'field for filtering by name', required=False,
                      type=openapi.TYPE_STRING)
], responses={
    200: 'result',
    400: 'bad request'
})
@api_view(['POST', 'GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def university_crud(request):
    if request.method == "POST":
        serializer = UniversitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("created", status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":
        data = University.objects.all()
        filterset_class = UniversityFilter
        filterset = filterset_class(request.GET, queryset=data)
        if filterset.is_valid():
            data = filterset.qs

        search = request.GET.get('search', None)
        if search:
            data = data.filter(name__icontains=search) | data.filter(address__icontains=search)

        serializer = UniversityGetSerializer(data, many=True)

        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def university_detail(request, pk):
    try:
        university = University.objects.get(pk=pk)
    except University.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UniversityGetSerializer(university)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UniversitySerializer(university, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        university.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='post', request_body=SubjectSerializer)
@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('search', openapi.IN_QUERY, 'field for search', required=False,
                      type=openapi.TYPE_STRING),
    openapi.Parameter('teacher', openapi.IN_QUERY, 'field for filtering by teacher id', required=False,
                      type=openapi.TYPE_INTEGER)
], responses={
    200: 'result',
    400: 'bad request'
})
@api_view(['POST', 'GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def subject_crud(request):
    if request.method == 'POST':
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("created", status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        data = Subject.objects.all()
        filterset_class = SubjectFilter
        filterset = filterset_class(request.GET, queryset=data)
        if filterset.is_valid():
            data = filterset.qs

        search = request.GET.get('search', None)
        if search:
            data = data.filter(name__icontains=search)
        serializer = SubjectGetSerializer(data, many=True)

        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def subject_detail(request, pk):
    try:
        subject = Subject.objects.get(pk=pk)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SubjectGetSerializer(subject)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='post', request_body=MeetingSerializer)
@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('subject', openapi.IN_QUERY, 'field for filtering by subject id', required=False,
                      type=openapi.TYPE_INTEGER)
], responses={
    200: 'result',
    400: 'bad request'
})
@api_view(['POST', 'GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def meeting_crud(request):
    if request.method == 'POST':
        serializer = MeetingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("created", status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        data = Meeting.objects.all()
        filterset_class = MeetingFilter
        filterset = filterset_class(request.GET, queryset=data)
        if filterset.is_valid():
            data = filterset.qs
        serializer = MeetingGetSerializer(data, many=True)

        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def meeting_detail(request, pk):
    try:
        meeting = Meeting.objects.get(pk=pk)
    except Meeting.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':

        serializer = MeetingGetSerializer(meeting)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MeetingSerializer(meeting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        meeting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('search', openapi.IN_QUERY, 'field for search', required=False,
                      type=openapi.TYPE_STRING)
], responses={
    200: 'result',
    400: 'bad request'
}, operation_description="search for all entities")
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def search_all(request):
    search = request.GET.get('search', None)
    if search:
        subjects = Subject.objects.filter(name__contains=search)
        teachers = Teacher.objects.filter((Q(first_name__icontains=search) | Q(last_name__icontains=search)
                                           | Q(username__icontains=search)) & Q(user_type__icontains="teacher"))
        universities = University.objects.filter(name__icontains=search)

        results = {
            "subjects": list(subjects.values()),
            "teachers": list(teachers.values()),
            "universities": list(universities.values())
        }

        return Response(results, status=status.HTTP_200_OK)

    return Response({"detail": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', request_body=TeacherSerializer, operation_description="Create teacher")
@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('search', openapi.IN_QUERY, 'field for search', required=False,
                      type=openapi.TYPE_STRING),
    openapi.Parameter('university', openapi.IN_QUERY, 'field for filtering by university id', required=False,
                      type=openapi.TYPE_STRING)
], responses={
    200: 'result',
    400: 'bad request'
})
@api_view(['POST', 'GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def teacher_crud(request):
    if request.method == 'POST':
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            teacher = Teacher.objects.get(username=request.data['username'])
            teacher.user_type = "teacher"
            password = generate_password()
            teacher.set_password(password)
            teacher.save()
            data = serializer.data
            data['password'] = password
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        data = Teacher.objects.all()
        filterset_class = TeacherFilter

        filterset = filterset_class(request.GET, queryset=data)
        if filterset.is_valid():
            data = filterset.qs
        serializer = TeacherGetSerializer(data, many=True)
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
def teacher_detail(request, pk):
    try:
        teacher = Teacher.objects.get(pk=pk)
    except Teacher.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':

        serializer = TeacherGetSerializer(teacher)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TeacherSerializer(teacher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        teacher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

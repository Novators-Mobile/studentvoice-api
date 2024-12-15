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

signup_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'second_name': openapi.Schema(type=openapi.TYPE_STRING),
        'patronymic': openapi.Schema(type=openapi.TYPE_STRING)
    }
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
                     request_body=signup_body,
                     responses={
                         200: 'token',
                         400: 'username and password must be provided'
                     })
@api_view(['POST'])
def signup(request):
    if 'username' not in request.data or 'password' not in request.data:
        return Response({"detail": "username and password must be provided"}, status=status.HTTP_400_BAD_REQUEST)

    user_exists = CustomUser.objects.filter(username=request.data['username']).first()
    if user_exists:
        return Response({"detail": "user already exist"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = SignUpSerializer(data=request.data)
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


@swagger_auto_schema(method='post', request_body=UniversitySerializer,
                     responses={
                         201: 'created',
                         400: 'bad request'
                     })
@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('search', openapi.IN_QUERY, 'field for search', required=False,
                      type=openapi.TYPE_STRING),
    openapi.Parameter('name', openapi.IN_QUERY, 'field for filtering by name', required=False,
                      type=openapi.TYPE_STRING)
], responses={
    200: UniversityGetSerializer.many_init(),
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
            search = search.lower()
            data = data.filter(name__icontains=search)

        serializer = UniversityGetSerializer(data, many=True)

        return Response(serializer.data)


@swagger_auto_schema(method='get', responses={
    404: 'not found',
    200: UniversityGetSerializer
})
@swagger_auto_schema(method='put', request_body=UniversitySerializer,
                     responses={
                         200: UniversitySerializer,
                         404: 'not found'
                     })
@swagger_auto_schema(method='delete',
                     responses={
                         204: 'deleted',
                         404: 'not found'
                     })
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


@swagger_auto_schema(method='post', request_body=SubjectSerializer,
                     responses={
                         201: 'created',
                         400: 'bad request'
                     })
@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('search', openapi.IN_QUERY, 'field for search by name', required=False,
                      type=openapi.TYPE_STRING),
    openapi.Parameter('teacher', openapi.IN_QUERY, 'field for filtering by teacher id', required=False,
                      type=openapi.TYPE_INTEGER),
    openapi.Parameter('university', openapi.IN_QUERY, 'field for filtering by university id',
                      required=False, type=openapi.TYPE_INTEGER)
], responses={
    200: SubjectGetSerializer.many_init(),
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
        teacher = request.GET.get('teacher', None)
        if teacher:
            data = data.filter(teachers__in=[teacher])

        university = request.GET.get('university', None)
        if university:
            data = data.filter(university__id=university)
        search = request.GET.get('search', None)
        if search:
            search = search.lower()
            data = data.filter(name__icontains=search)
        serializer = SubjectGetSerializer(data, many=True)

        return Response(serializer.data)


@swagger_auto_schema(method='get', responses={
    200: SubjectGetSerializer,
    404: 'not found'
})
@swagger_auto_schema(method='put', request_body=SubjectSerializer,
                     responses={
                         200: SubjectSerializer,
                         404: 'not found'
                     })
@swagger_auto_schema(method='delete',
                     responses={
                         204: 'no content',
                         404: 'not found'
                     })
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


@swagger_auto_schema(method='post', operation_description='add teacher to a subject',
                     responses={
                         200: 'teacher added',
                         404: 'not found'
                     })
@swagger_auto_schema(method='delete', operation_description='remove teacher from subject',
                     responses={
                         204: 'removed',
                         404: 'teacher not found'
                     })
@api_view(['POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def subject_teacher_operations(request, pk, teacher_id):
    try:
        subject = Subject.objects.get(pk=pk)
        teacher = Teacher.objects.get(pk=teacher_id)
    except Subject.DoesNotExist:
        return Response('subject not found', status=status.HTTP_404_NOT_FOUND)
    except Teacher.DoesNotExist:
        return Response('teacher not found', status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        subject.teachers.add(teacher)
        return Response('teacher added')
    elif request.method == 'DELETE':
        if teacher not in subject.teachers.all():
            return Response('teacher not found in this subject', status=status.HTTP_404_NOT_FOUND)
        subject.teachers.remove(teacher)
        return Response('removed', status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='post', request_body=MeetingSerializer,
                     responses={
                         201: 'created',
                         400: 'bad request'
                     }, operation_description='я хз почему teacher это строка)), сюда просто id учителя вставлять')
@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('subject', openapi.IN_QUERY, 'field for filtering by subject id', required=False,
                      type=openapi.TYPE_INTEGER),
    openapi.Parameter('teacher', openapi.IN_QUERY, 'field for filtering by teacher id', required=False,
                      type=openapi.TYPE_INTEGER),
    openapi.Parameter('type', openapi.IN_QUERY, 'field for filtering by type (lecture or practice)', required=False,
                      type=openapi.TYPE_STRING),
    openapi.Parameter('search', openapi.IN_QUERY, 'field for searching by name', required=False,
                      type=openapi.TYPE_STRING)
], responses={
    200: MeetingGetSerializer.many_init(),
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
        subject = request.GET.get('subject', None)
        if subject:
            data = data.filter(subject_id=subject)
        teacher = request.GET.get('teacher', None)
        if teacher:
            data = data.filter(teacher_id=teacher)
        subject_type = request.GET.get('type', None)
        if subject_type:
            data = data.filter(type=subject_type)

        search = request.GET.get('search', None)
        if search:
            search = search.lower()
            data = data.filter(name__icontains=search)
        serializer = MeetingGetSerializer(data, many=True)

        return Response(serializer.data)


@swagger_auto_schema(method='get', responses={
    200: MeetingGetSerializer,
    404: 'not found'
})
@swagger_auto_schema(method='put', request_body=MeetingSerializer,
                     responses={
                         200: MeetingSerializer,
                         404: 'not found'
                     })
@swagger_auto_schema(method='delete', responses={
    204: 'no content',
    404: 'not found'
})
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
    200: SearchResultSerializer,
    400: 'bad request'
}, operation_description="search for all entities")
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def search_all(request):
    search = request.GET.get('search', None)
    if search:
        search = search.lower()
        subjects = Subject.objects.filter(name__contains=search)
        teachers = Teacher.objects.filter((Q(first_name__icontains=search) | Q(second_name__icontains=search)
                                           | Q(patronymic__icontains=search)
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
                      type=openapi.TYPE_STRING),
    openapi.Parameter('subject', openapi.IN_QUERY, 'field for filtering by subject id', required=False,
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
        subject_id = request.GET.get('subject', None)
        search = request.GET.get('search', None)
        if search:
            search = search.lower()
            data = data.filter((Q(first_name__icontains=search) | Q(second_name__icontains=search)
                                | Q(patronymic__icontains=search)
                                | Q(username__icontains=search)) & Q(user_type__icontains="teacher"))
        if subject_id is not None:
            data = data.filter(subject__id=subject_id)
            serializer = TeacherGetSerializer(data, many=True)
            return Response(serializer.data)
        else:
            filterset = filterset_class(request.GET, queryset=data)
            if filterset.is_valid():
                data = filterset.qs
            serializer = TeacherGetSerializer(data, many=True)
            return Response(serializer.data)


@swagger_auto_schema(method='get', responses={
    200: TeacherGetSerializer,
    404: 'not found'
})
@swagger_auto_schema(method='put', request_body=TeacherSerializer, responses={
    200: TeacherSerializer,
    404: 'not found',
    400: 'bad request'
})
@swagger_auto_schema(method='delete', responses={
    204: 'no content',
    404: 'not found'
})
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

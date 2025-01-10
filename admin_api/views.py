import calendar

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .filters import TeacherFilter
import datetime
from django.utils import timezone
from calendar import monthrange
from .serializers import *
from .decorators import admin_required
from rest_framework import status
from .models import CustomUser, University
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import generate_password
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from .authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from os import getenv

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
    openapi.Parameter('search', openapi.IN_QUERY, 'field for search by name or short name', required=False,
                      type=openapi.TYPE_STRING),
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

        search = request.GET.get('search', None)
        if search:
            search = search.lower()
            data = data.filter(name__icontains=search) | data.filter(short_name__icontains=search)

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


@swagger_auto_schema(method='get', responses={
    404: 'not found',
    200: MonthStatisticsSerializer
}, operation_description='get institute statistics by months')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def university_month_statistics(request, pk):
    try:
        university = University.objects.get(pk=pk)
    except University.DoesNotExist:
        return Response("not found", status=status.HTTP_404_NOT_FOUND)

    subjects = Subject.objects.filter(university=university.pk).all()
    subjects = [subject.pk for subject in subjects]
    data = {'months': []}
    current_datetime = timezone.now()

    for month in range(12):
        month_range = monthrange(current_datetime.year, current_datetime.month)
        datetime_max = current_datetime.replace(day=month_range[1])
        datetime_min = current_datetime.replace(day=1)
        month_meetings = Meeting.objects.filter(date__range=(datetime_min, datetime_max), subject__in=subjects).all()
        meetings_serializer = MeetingGetSerializer(month_meetings, many=True)
        month_ratings = [meeting['rating'] for meeting in meetings_serializer.data if meeting['rating'] > 0]
        if len(month_ratings) > 0:
            data['months'].append({"name": current_datetime.strftime("%B"),
                                   "rating": sum(month_ratings) / len(month_ratings),
                                   "year": str(current_datetime.year)})

        current_datetime = datetime_min - timezone.timedelta(days=1)

    serializer = MonthStatisticsSerializer(data=data)
    if serializer.is_valid():
        return Response(serializer.data)


@swagger_auto_schema(method='get', responses={
    404: 'not found',
    200: WeekStatisticsSerializer
}, operation_description='get institute statistics by weeks in month',
                     manual_parameters=[
                         openapi.Parameter('year', openapi.IN_QUERY, 'needed year',
                                           required=True,
                                           type=openapi.TYPE_STRING),
                         openapi.Parameter('month', openapi.IN_QUERY, 'needed month (January, February, etc)',
                                           required=True,
                                           type=openapi.TYPE_STRING),
                     ])
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def university_weeks_in_month_statistics(request, pk):
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    university = pk
    if year is None or month is None or university is None:
        return Response("bad request: year or month or university is not specified",
                        status=status.HTTP_400_BAD_REQUEST)
    if month in calendar.month_name:
        month_number = list(calendar.month_name).index(month)
    else:
        return Response("bad request: wrong month name", status=status.HTTP_400_BAD_REQUEST)

    if not year.isdigit():
        return Response("bad request: wrong year", status=status.HTTP_400_BAD_REQUEST)

    start_datetime = timezone.datetime(year=int(year), month=month_number, day=1)
    if month_number == 12:
        end_datetime = timezone.datetime(year=int(year) + 1, month=1, day=1)
    else:
        end_datetime = timezone.datetime(year=int(year), month=month_number + 1, day=1)

    current = start_datetime
    data = {"weeks": []}
    subjects = Subject.objects.filter(university=university).all()
    subjects = [subject.pk for subject in subjects]
    week_number = 1
    while current < end_datetime:
        week_end = current + timezone.timedelta(days=6 - current.weekday())
        if week_end >= end_datetime:
            week_end = end_datetime - timezone.timedelta(days=1)
        week_meetings = Meeting.objects.filter(date__range=(current, week_end), subject__in=subjects).all()
        meetings_serializer = MeetingGetSerializer(week_meetings, many=True)
        week_ratings = [meeting['rating'] for meeting in meetings_serializer.data if meeting['rating'] > 0]
        if len(week_ratings) > 0:
            data['weeks'].append({"week_number": week_number,
                                  "rating": sum(week_ratings) / len(week_ratings)})
        else:
            data['weeks'].append({"week_number": week_number, "rating": None})
        week_number += 1
        current = week_end + timezone.timedelta(days=1)

    return Response(data)


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
            data = data.filter(lecture_teachers__in=[teacher]) | data.filter(practice_teachers__in=[teacher])

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
def subject_teacher_operations_lecture(request, pk, teacher_id):
    try:
        subject = Subject.objects.get(pk=pk)
        teacher = Teacher.objects.get(pk=teacher_id)
    except Subject.DoesNotExist:
        return Response('subject not found', status=status.HTTP_404_NOT_FOUND)
    except Teacher.DoesNotExist:
        return Response('teacher not found', status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        subject.lecture_teachers.add(teacher)
        subject.save()
        return Response('teacher added')
    elif request.method == 'DELETE':
        if teacher.pk not in [teacher.pk for teacher in subject.lecture_teachers.all()]:
            return Response('teacher not found in this subject', status=status.HTTP_404_NOT_FOUND)
        subject.lecture_teachers.remove(teacher)
        subject.save()
        return Response('removed', status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
@admin_required
def subject_teacher_operations_practice(request, pk, teacher_id):
    try:
        subject = Subject.objects.get(pk=pk)
        teacher = Teacher.objects.get(pk=teacher_id)
    except Subject.DoesNotExist:
        return Response('subject not found', status=status.HTTP_404_NOT_FOUND)
    except Teacher.DoesNotExist:
        return Response('teacher not found', status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        subject.practice_teachers.add(teacher)
        subject.save()
        return Response('teacher added')
    elif request.method == 'DELETE':
        if teacher.pk not in [teacher.pk for teacher in subject.practice_teachers.all()]:
            return Response('teacher not found in this subject', status=status.HTTP_404_NOT_FOUND)
        subject.practice_teachers.remove(teacher)
        subject.save()
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
        subjects = Subject.objects.filter(name__icontains=search)
        teachers = Teacher.objects.filter((Q(first_name__icontains=search) | Q(second_name__icontains=search)
                                           | Q(patronymic__icontains=search)
                                           | Q(username__icontains=search)))
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
        if 'lecture_subjects' in serializer.initial_data:
            lecture_subjects = serializer.initial_data.pop('lecture_subjects')
        else:
            lecture_subjects = []
        if 'practice_subjects' in serializer.initial_data:
            practice_subjects = serializer.initial_data.pop('practice_subjects')
        else:
            practice_subjects = []
        if serializer.is_valid():
            serializer.save()
            teacher = Teacher.objects.get(username=request.data['username'])
            teacher.user_type = "teacher"
            password = generate_password()
            teacher.set_password(password)
            teacher.save()

            data = serializer.data
            lecture_subjects = Subject.objects.filter(pk__in=lecture_subjects).all()
            for subject in lecture_subjects:
                subject.lecture_teachers.add(teacher)
                subject.save()

            practice_subjects = Subject.objects.filter(pk__in=practice_subjects).all()
            for subject in practice_subjects:
                subject.practice_teachers.add(teacher)
                subject.save()
            data['password'] = password
            html_content = render_to_string('new_user.html', {'password': password})
            email = EmailMessage(
                'Данные для входа в StudentVoice',
                html_content,
                'StudentVoice',
                [data['email']]
            )
            email.content_subtype = "html"
            email.send()
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        data = Teacher.objects.all()
        subject_id = request.GET.get('subject', None)
        search = request.GET.get('search', None)
        university = request.GET.get('university', None)
        if search:
            search = search.lower()
            data = data.filter((Q(first_name__icontains=search) | Q(second_name__icontains=search)
                                | Q(patronymic__icontains=search)
                                | Q(username__icontains=search)))
        if subject_id:
            try:
                if university:
                    subject = Subject.objects.get(pk=subject_id, university=university)
                else:
                    subject = Subject.objects.get(pk=subject_id)
            except Subject.DoesNotExist:
                return Response([])
            lecture_teachers = [teacher.pk for teacher in subject.lecture_teachers.all()]
            practice_teachers = [teacher.pk for teacher in subject.practice_teachers.all()]
            teachers = Teacher.objects.filter(
                Q(pk__in=lecture_teachers) | Q(pk__in=practice_teachers)).all()
            if search:
                search = search.lower()
                teachers = teachers.filter((Q(first_name__icontains=search) | Q(second_name__icontains=search)
                                    | Q(patronymic__icontains=search)
                                    | Q(username__icontains=search)))
            serializer = TeacherGetSerializer(teachers, many=True)
            return Response(serializer.data)

        if university:
            data = data.filter(university=university)

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
        if 'lecture_subjects' in serializer.initial_data:
            lecture_subjects = serializer.initial_data.pop('lecture_subjects')
            old_lecture_subjects = Subject.objects.filter(lecture_teachers__in=[pk]).all()
            for old_subject in old_lecture_subjects:
                old_subject.lecture_teachers.remove(pk)
                old_subject.save()
            lecture_subjects = Subject.objects.filter(pk__in=lecture_subjects).all()
            for subject in lecture_subjects:
                subject.lecture_teachers.add(pk)
                subject.save()
        if 'practice_subjects' in serializer.initial_data:
            practice_subjects = serializer.initial_data.pop('practice_subjects')
            old_practice_subjects = Subject.objects.filter(practice_teachers__in=[pk]).all()
            for old_subject in old_practice_subjects:
                old_subject.practice_teachers.remove(pk)
                old_subject.save()

            practice_subjects = Subject.objects.filter(pk__in=practice_subjects).all()
            for subject in practice_subjects:
                subject.practice_teachers.add(pk)
                subject.save()
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        teacher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

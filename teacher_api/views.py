from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from admin_api.authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from admin_api.models import Meeting, Teacher, Subject
from admin_api.serializers import MeetingGetSerializer, TeacherGetSerializer, SubjectGetSerializer
from rest_framework.response import Response
from admin_api.serializers import MeetingSerializer
from polls.serializers import MeetingWithTeacherGetSerializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import MeetingPutSerializer, PollParticipantSerializer
from django.db.models import Q
from polls.models import PollResult


@swagger_auto_schema(method='post', request_body=MeetingSerializer,
                     responses={
                         201: 'created',
                         400: 'bad request'
                     },
                     operation_description
                     ='teacher ни на что не влияет, подхватывается айди текущего юзера, прост заглушка')
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
def meeting_crud(request):
    current_user = request.user
    if request.method == 'GET':
        data = Meeting.objects.filter(teacher__in=[current_user.id]).all()
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

    elif request.method == 'POST':
        request.data['teacher'] = current_user.id
        serializer = MeetingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("created", status.HTTP_201_CREATED)

        return Response("Bad request", status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={
    200: MeetingWithTeacherGetSerializer,
    404: 'not found'
})
@swagger_auto_schema(method='put', request_body=MeetingPutSerializer,
                     responses={
                         200: MeetingPutSerializer,
                         404: 'not found'
                     })
@swagger_auto_schema(method='delete', responses={
    204: 'no content',
    404: 'not found'
})
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def meeting_detail(request, pk):
    try:
        meeting = Meeting.objects.get(pk=pk)
        if meeting.teacher.pk != request.user.id:
            return Response("access denied", status=status.HTTP_403_FORBIDDEN)
    except Meeting.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MeetingWithTeacherGetSerializer(meeting)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MeetingPutSerializer(meeting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        meeting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='get', responses={
    200: TeacherGetSerializer,
    404: 'not found'
}, operation_description='get info about current logged in teacher')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def teacher_me(request):
    try:
        teacher = Teacher.objects.get(pk=request.user.id)
    except Teacher.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TeacherGetSerializer(teacher)
    return Response(serializer.data)


@swagger_auto_schema(method='get', responses={
    200: SubjectGetSerializer,
    404: 'not found'
}, operation_description='get info about current logged in teacher\'s subject by id')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def subject_detail(request, pk):
    try:
        subject = Subject.objects.get(pk=pk)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SubjectGetSerializer(subject)
    return Response(serializer.data)


@swagger_auto_schema(method='get', responses={
    200: SubjectGetSerializer,
    404: 'not found'
}, operation_description='get info about current logged in teacher\'s subjects')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def get_teacher_subjects(request):
    current_user = request.user.id
    subjects = Subject.objects.filter(Q(lecture_teachers__in=[current_user])
                                      | Q(practice_teachers__in=[current_user])).distinct().all()
    serializer = SubjectGetSerializer(subjects, many=True)

    return Response(serializer.data)


@swagger_auto_schema(method='get', responses={
    200: PollParticipantSerializer,
    404: 'not found'
}, operation_description='get poll\'s participants')
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def get_polls_participants(request, meeting_id):
    poll_results = PollResult.objects.filter(poll=meeting_id).all()
    serializer = PollParticipantSerializer(poll_results, many=True)
    return Response(serializer.data)
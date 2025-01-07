from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from admin_api.authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from admin_api.models import Meeting
from admin_api.serializers import MeetingGetSerializer
from rest_framework.response import Response
from admin_api.serializers import MeetingSerializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import MeetingPutSerializer


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
    200: MeetingGetSerializer,
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
        serializer = MeetingGetSerializer(meeting)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MeetingPutSerializer(request.data)
        if serializer.is_valid():
            return Response(serializer.data)

    elif request.method == 'DELETE':
        meeting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

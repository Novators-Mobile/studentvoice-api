from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from admin_api.authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Poll, PollResult
from .serializers import PollSerializer, PollResultSerializer, PollGetSerializer


@swagger_auto_schema(method='post', request_body=PollSerializer)
@swagger_auto_schema(method='get',
                     responses={
                         200: PollGetSerializer.many_init(),
                         400: 'bad request'
                     })
@api_view(['POST', 'GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def poll_crud(request):
    if request.method == 'POST':
        serializer = PollSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("created", status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        data = Poll.objects.all()
        serializer = PollGetSerializer(data, many=True)

        return Response(serializer.data)


@swagger_auto_schema(method='get',
                     responses={
                         200: PollGetSerializer,
                         400: 'bad request'
                     })
@api_view(['GET'])
def poll_get(request, pk):
    try:
        poll = Poll.objects.get(pk=pk)
    except Poll.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PollGetSerializer(poll)
        return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=PollSerializer,
                     responses={
                         200: PollGetSerializer,
                         404: 'poll not found'
                     })
@swagger_auto_schema(method='delete',
                     responses={
                         204: 'no content',
                         404: 'poll not found'
                     })
@api_view(['PUT', 'DELETE'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def poll_detail(request, pk):
    try:
        poll = Poll.objects.get(pk=pk)
    except Poll.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = PollSerializer(poll, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        poll.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='get', operation_description="get all results from poll",
                     responses={
                         200: 'result',
                         400: 'bad request'
                     })
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def poll_result_crud(request, poll_pk):
    try:
        poll = Poll.objects.get(pk=poll_pk)
    except Poll.DoesNotExist:
        return Response({"detail": "Poll not found."}, status=status.HTTP_404_NOT_FOUND)
    data = request.data
    data['poll'] = poll.pk

    if request.method == 'GET':
        data = PollResult.objects.filter(poll=poll)
        serializer = PollResultSerializer(data, many=True)

        return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=PollResultSerializer, operation_description='send poll result',
                     responses={
                         201: 'created',
                         404: 'poll not found'
                     })
@api_view(['POST'])
def poll_result_post(request, poll_pk):
    try:
        poll = Poll.objects.get(pk=poll_pk)
    except Poll.DoesNotExist:
        return Response({"detail": "Poll not found."}, status=status.HTTP_404_NOT_FOUND)
    data = request.data
    data['poll'] = poll.pk
    if request.method == 'POST':

        serializer = PollResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("created", status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

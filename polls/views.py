from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from admin_api.authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from admin_api.models import Meeting
from .models import Form
from .serializers import FormSerializer
from .google_forms_worker import GoogleFormsWorker


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def form_detail(request, meeting_pk):
    try:
        meeting = Meeting.objects.get(pk=meeting_pk)
    except Meeting.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        form = Form.objects.filter(meeting_id=meeting_pk).first()
        if not form:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = FormSerializer(form)
        return Response(serializer.data)

    elif request.method == "POST":
        forms_worker = GoogleFormsWorker()
        form_id, form_url = forms_worker.create_form()
        if form_id is not None and form_url is not None:
            data = {
                "form_id": form_id,
                "form_url": form_url,
                "meeting": meeting_pk
            }
            serializer = FormSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response("created", status=status.HTTP_201_CREATED)

        return Response("error happened", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
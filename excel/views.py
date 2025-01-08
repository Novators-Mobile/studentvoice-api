from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from admin_api.authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from admin_api.models import University, Subject, Meeting, Teacher
from admin_api import serializers
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from datetime import datetime


@swagger_auto_schema(method='get',
                     responses={
                         200: '',
                         400: 'bad request'
                     })
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def institute_to_subject(request, insitute_id):
    try:
        institute = University.objects.get(pk=insitute_id)
    except University.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    subjects = Subject.objects.filter(university=insitute_id).all()
    serializer = serializers.SubjectGetSerializer(subjects, many=True)
    data = list(map(lambda x: [x['name'], x['rating']], serializer.data))
    if len(data) == 0:
        return Response(status=status.HTTP_204_NO_CONTENT)

    header = NamedStyle(name="Заголовок документа", number_format="General",
                        font=Font(name='Times New Roman', bold=True, size=24),
                        alignment=Alignment(horizontal="left", vertical="bottom"))
    general = NamedStyle(name="Общий", number_format="General", font=Font(name='Times New Roman', bold=False, size=12),
                         alignment=Alignment(horizontal="left", vertical="bottom"))
    tableheader = NamedStyle(name="Заголовок таблицы", number_format="General",
                             font=Font(name='Times New Roman', bold=True, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))
    numberStyle = NamedStyle(name="Числа", number_format="0.0", font=Font(name='Times New Roman', bold=False, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))

    workbook = Workbook()
    sheet = workbook.active

    sheet.row_dimensions[1].height = 30
    sheet.column_dimensions['A'].width = 43

    sheet.cell(1, 1, 'Отчет по' + institute.name).style = header
    sheet.cell(2, 1, 'Дата и время обращения: ' + datetime.now().strftime("%d.%m.%Y %H:%M")).style = general
    sheet.cell(4, 1, 'Дисциплина').style = tableheader
    sheet.cell(4, 2, 'Балл').style = tableheader

    lastrow = 5
    for row in data:
        sheet.cell(lastrow, 1, row[0]).style = general
        sheet.cell(lastrow, 2, row[1]).style = numberStyle
        lastrow += 1
    sheet.auto_filter.ref = 'A4:B' + str(lastrow)

    workbook.save("export.xlsx")
    with open('export.xlsx', 'rb') as f:
        file_data = f.read()
    response = HttpResponse(file_data, content_type='application/vnd.ms-excel',
                            headers={"Content-Disposition": f'attachment; filename="export.xlsx"'})

    return response


@swagger_auto_schema(method='get',
                     responses={
                         200: '',
                         400: 'bad request'
                     })
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def institute_to_teacher(request, insitute_id):
    try:
        institute = University.objects.get(pk=insitute_id)
    except University.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    teachers = Teacher.objects.filter(university=insitute_id).all()
    serializer = serializers.TeacherGetSerializer(teachers, many=True)
    data = list(map(lambda x: [x['rating'], x['second_name'], x['first_name'], x['patronymic']], serializer.data))
    if len(data) == 0:
        return Response(status=status.HTTP_204_NO_CONTENT)

    header = NamedStyle(name="Заголовок документа", number_format="General",
                        font=Font(name='Times New Roman', bold=True, size=24),
                        alignment=Alignment(horizontal="left", vertical="bottom"))
    general = NamedStyle(name="Общий", number_format="General", font=Font(name='Times New Roman', bold=False, size=12),
                         alignment=Alignment(horizontal="left", vertical="bottom"))
    tableheader = NamedStyle(name="Заголовок таблицы", number_format="General",
                             font=Font(name='Times New Roman', bold=True, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))
    numberStyle = NamedStyle(name="Числа", number_format="0.0", font=Font(name='Times New Roman', bold=False, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))

    workbook = Workbook()
    sheet = workbook.active

    sheet.row_dimensions[1].height = 30
    sheet.column_dimensions['A'].width = 43

    sheet.cell(1, 1, 'Отчет по' + institute.name).style = header
    sheet.cell(2, 1, 'Дата и время обращения: ' + datetime.now().strftime("%d.%m.%Y %H:%M")).style = general
    sheet.cell(4, 1, 'Преподаватель').style = tableheader
    sheet.cell(4, 2, 'Балл').style = tableheader

    lastrow = 5
    for row in data:
        sheet.cell(lastrow, 1, row[1] + " " + row[2] + " " + row[3]).style = general
        sheet.cell(lastrow, 2, row[0]).style = numberStyle
        lastrow += 1
    sheet.auto_filter.ref = 'A4:B' + str(lastrow)
    workbook.save("export.xlsx")
    with open('export.xlsx', 'rb') as f:
        file_data = f.read()
    response = HttpResponse(file_data, content_type='application/vnd.ms-excel',
                            headers={"Content-Disposition": f'attachment; filename="export.xlsx"'})

    return response


@swagger_auto_schema(method='get',
                     responses={
                         200: '',
                         400: 'bad request'
                     })
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def subject_to_teacher(request, subject_id):
    try:
        subject = Subject.objects.get(pk=subject_id)
    except University.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    teachers = Teacher.objects.filter(subject=subject_id).all()
    serializer = serializers.TeacherGetSerializer(teachers, many=True)
    data = list(map(lambda x: [x['rating'], x['second_name'], x['first_name'], x['patronymic']], serializer.data))
    if len(data) == 0:
        return Response(status=status.HTTP_204_NO_CONTENT)

    header = NamedStyle(name="Заголовок документа", number_format="General",
                        font=Font(name='Times New Roman', bold=True, size=24),
                        alignment=Alignment(horizontal="left", vertical="bottom"))
    general = NamedStyle(name="Общий", number_format="General", font=Font(name='Times New Roman', bold=False, size=12),
                         alignment=Alignment(horizontal="left", vertical="bottom"))
    tableheader = NamedStyle(name="Заголовок таблицы", number_format="General",
                             font=Font(name='Times New Roman', bold=True, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))
    numberStyle = NamedStyle(name="Числа", number_format="0.0", font=Font(name='Times New Roman', bold=False, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))

    workbook = Workbook()
    sheet = workbook.active

    sheet.row_dimensions[1].height = 30
    sheet.column_dimensions['A'].width = 43

    sheet.cell(1, 1, 'Отчет по' + subject.name).style = header
    sheet.cell(2, 1, 'Дата и время обращения: ' + datetime.now().strftime("%d.%m.%Y %H:%M")).style = general
    sheet.cell(4, 1, 'Преподаватель').style = tableheader
    sheet.cell(4, 2, 'Балл').style = tableheader

    lastrow = 5
    for row in data:
        sheet.cell(lastrow, 1, row[1] + row[2] + row[3]).style = general
        sheet.cell(lastrow, 2, row[0]).style = numberStyle
        lastrow += 1
    sheet.auto_filter.ref = 'A4:B' + str(lastrow)
    workbook.save("export.xlsx")
    with open('export.xlsx', 'rb') as f:
        file_data = f.read()
    response = HttpResponse(file_data, content_type='application/vnd.ms-excel',
                            headers={"Content-Disposition": f'attachment; filename="export.xlsx"'})

    return response


@swagger_auto_schema(method='get',
                     responses={
                         200: '',
                         204: 'no content',
                         400: 'bad request'
                     })
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def subject_to_meeting(request, subject_id):
    try:
        subject = Subject.objects.get(pk=subject_id)
    except University.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    meetings = Meeting.objects.filter(subject=subject_id).all()
    serializer = serializers.MeetingGetSerializer(meetings, many=True)
    data = list(map(lambda x: [x['name'], x['rating']], serializer.data))
    if len(data) == 0:
        return Response(status=status.HTTP_204_NO_CONTENT)

    header = NamedStyle(name="Заголовок документа", number_format="General",
                        font=Font(name='Times New Roman', bold=True, size=24),
                        alignment=Alignment(horizontal="left", vertical="bottom"))
    general = NamedStyle(name="Общий", number_format="General", font=Font(name='Times New Roman', bold=False, size=12),
                         alignment=Alignment(horizontal="left", vertical="bottom"))
    tableheader = NamedStyle(name="Заголовок таблицы", number_format="General",
                             font=Font(name='Times New Roman', bold=True, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))
    numberStyle = NamedStyle(name="Числа", number_format="0.0", font=Font(name='Times New Roman', bold=False, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))

    workbook = Workbook()
    sheet = workbook.active

    sheet.row_dimensions[1].height = 30
    sheet.column_dimensions['A'].width = 43

    sheet.cell(1, 1, 'Отчет по' + subject.name).style = header
    sheet.cell(2, 1, 'Дата и время обращения: ' + datetime.now().strftime("%d.%m.%Y %H:%M")).style = general
    sheet.cell(4, 1, 'Дисциплина').style = tableheader
    sheet.cell(4, 2, 'Балл').style = tableheader

    lastrow = 5
    for row in data:
        sheet.cell(lastrow, 1, row[0]).style = general
        sheet.cell(lastrow, 2, row[1]).style = numberStyle
        lastrow += 1
    sheet.auto_filter.ref = 'A4:B' + str(lastrow)
    workbook.save("export.xlsx")
    with open('export.xlsx', 'rb') as f:
        file_data = f.read()
    response = HttpResponse(file_data, content_type='application/vnd.ms-excel',
                            headers={"Content-Disposition": f'attachment; filename="export.xlsx"'})

    return response


@swagger_auto_schema(method='get',
                     responses={
                         200: '',
                         204: 'No content',
                         400: 'bad request'
                     })
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def teacher_to_subject(request, teacher_id):
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except University.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    subjects = Subject.objects.filter(teachers__in=[teacher_id]).all()
    serializer = serializers.SubjectGetSerializer(subjects, many=True)
    data = list(map(lambda x: [x['name'], x['rating']], serializer.data))
    if len(data) == 0:
        return Response(status=status.HTTP_204_NO_CONTENT)

    header = NamedStyle(name="Заголовок документа", number_format="General",
                        font=Font(name='Times New Roman', bold=True, size=24),
                        alignment=Alignment(horizontal="left", vertical="bottom"))
    general = NamedStyle(name="Общий", number_format="General", font=Font(name='Times New Roman', bold=False, size=12),
                         alignment=Alignment(horizontal="left", vertical="bottom"))
    tableheader = NamedStyle(name="Заголовок таблицы", number_format="General",
                             font=Font(name='Times New Roman', bold=True, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))
    numberStyle = NamedStyle(name="Числа", number_format="0.0", font=Font(name='Times New Roman', bold=False, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))

    workbook = Workbook()
    sheet = workbook.active

    sheet.row_dimensions[1].height = 30
    sheet.column_dimensions['A'].width = 43

    sheet.cell(1, 1, 'Отчет по {} {} {}'.format(teacher.last_name, teacher.first_name, teacher.patronymic)).style = header
    sheet.cell(2, 1, 'Дата и время обращения: ' + datetime.now().strftime("%d.%m.%Y %H:%M")).style = general
    sheet.cell(4, 1, 'Пара').style = tableheader
    sheet.cell(4, 2, 'Балл').style = tableheader

    lastrow = 5
    for row in data:
        sheet.cell(lastrow, 1, row[0]).style = general
        sheet.cell(lastrow, 2, row[1]).style = numberStyle
        lastrow += 1
    sheet.auto_filter.ref = 'A4:B' + str(lastrow)

    workbook.save("export.xlsx")
    with open('export.xlsx', 'rb') as f:
        file_data = f.read()
    response = HttpResponse(file_data, content_type='application/vnd.ms-excel',
                            headers={"Content-Disposition": f'attachment; filename="export.xlsx"'})

    return response


@swagger_auto_schema(method='get',
                     responses={
                         200: '',
                         400: 'bad request'
                     })
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def teacher_to_meeting(request, teacher_id):
    try:
        teacher = Teacher.objects.get(pk=teacher_id)
    except University.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    meetings = Meeting.objects.filter(teacher=teacher_id).all()
    serializer = serializers.MeetingGetSerializer(meetings, many=True)
    data = list(map(lambda x: [x['name'], x['rating']], serializer.data))
    if len(data) == 0:
        return None

    header = NamedStyle(name="Заголовок документа", number_format="General",
                        font=Font(name='Times New Roman', bold=True, size=24),
                        alignment=Alignment(horizontal="left", vertical="bottom"))
    general = NamedStyle(name="Общий", number_format="General", font=Font(name='Times New Roman', bold=False, size=12),
                         alignment=Alignment(horizontal="left", vertical="bottom"))
    tableheader = NamedStyle(name="Заголовок таблицы", number_format="General",
                             font=Font(name='Times New Roman', bold=True, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))
    numberStyle = NamedStyle(name="Числа", number_format="0.0", font=Font(name='Times New Roman', bold=False, size=12),
                             alignment=Alignment(horizontal="left", vertical="bottom"))

    workbook = Workbook()
    sheet = workbook.active

    sheet.row_dimensions[1].height = 30
    sheet.column_dimensions['A'].width = 43

    sheet.cell(1, 1, 'Отчет по {} {} {}'.format(teacher.last_name, teacher.first_name, teacher.patronymic)).style = header
    sheet.cell(2, 1, 'Дата и время обращения: ' + datetime.now().strftime("%d.%m.%Y %H:%M")).style = general
    sheet.cell(4, 1, 'Дисциплина').style = tableheader
    sheet.cell(4, 2, 'Балл').style = tableheader

    lastrow = 5
    for row in data:
        sheet.cell(lastrow, 1, row[0]).style = general
        sheet.cell(lastrow, 2, row[1]).style = numberStyle
        lastrow += 1
    sheet.auto_filter.ref = 'A4:B' + str(lastrow)

    workbook.save("export.xlsx")
    with open('export.xlsx', 'rb') as f:
        file_data = f.read()
    response = HttpResponse(file_data, content_type='application/vnd.ms-excel',
                            headers={"Content-Disposition": f'attachment; filename="export.xlsx"'})

    return response

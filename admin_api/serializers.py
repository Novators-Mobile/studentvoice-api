from rest_framework import serializers
from .models import CustomUser, University, Subject, Meeting, Teacher
from polls.models import Poll
from statistics import mean


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['id', 'first_name', 'second_name', 'patronymic', 'user_type']


class SignUpSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = CustomUser
        fields = ['id', 'first_name', 'second_name', 'patronymic', 'user_type', 'username', 'password']


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['name', 'short_name']


class UniversityGetSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    teachers_rating = serializers.SerializerMethodField()
    subjects_rating = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = ['id', 'name', 'short_name', 'rating', 'teachers_rating', 'subjects_rating']

    def get_rating(self, obj):
        subjects = Subject.objects.filter(university=obj.id).all()
        if subjects:
            subject_ids = []
            for subject in subjects:
                subject_ids.append(subject.pk)
            meetings = Meeting.objects.filter(subject__in=subject_ids).all()
            meeting_ids = []
            for meeting in meetings:
                meeting_ids.append(meeting.pk)
            polls = Poll.objects.filter(pk__in=meeting_ids).all()
            poll_ratings = polls.values('question1_avg_mark', 'question2_avg_mark', 'question3_avg_mark',
                                        'question4_avg_mark', 'question5_avg_mark')
            poll_ratings = list(map(lambda x: sum(x.values()) / 5, poll_ratings))
            if len(poll_ratings) == 0:
                return None
            return mean(poll_ratings)
        return None

    def get_teachers_rating(self, obj):
        teachers = Teacher.objects.filter(university=obj.id).all()
        serializer = TeacherGetSerializer(teachers, many=True)
        data = list(map(lambda x: x['rating'], serializer.data))
        if len(data) == 0:
            return None
        return mean(data)

    def get_subjects_rating(self, obj):
        subjects = Subject.objects.filter(university=obj.id).all()
        serializer = SubjectGetSerializer(subjects, many=True)
        data = list(map(lambda x: x['rating'], serializer.data))
        if len(data) == 0:
            return None
        return mean(data)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['university', 'name']


class SubjectGetSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'teachers', 'university', 'name', 'rating']

    def get_rating(self, obj):
        meetings = Meeting.objects.filter(subject=obj.id).all()
        meeting_ids = []
        for meeting in meetings:
            meeting_ids.append(meeting.pk)

        if len(meeting_ids) == 0:
            return None
        polls = Poll.objects.filter(pk__in=meeting_ids).all()
        poll_ratings = polls.values('question1_avg_mark', 'question2_avg_mark', 'question3_avg_mark',
                                    'question4_avg_mark', 'question5_avg_mark')
        poll_ratings = list(map(lambda x: sum(x.values()) / 5, poll_ratings))
        if len(poll_ratings) == 0:
            return None
        return mean(poll_ratings)


class MeetingSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        poll = Poll.objects.create()
        return Meeting.objects.create(**validated_data, poll=poll)

    class Meta:
        model = Meeting
        fields = ['subject', 'date', 'teacher', 'type']


class MeetingGetSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = ['id', 'subject', 'date', 'poll', 'teacher', 'type', 'rating']

    def get_rating(self, obj):
        poll = Poll.objects.get(pk=obj.id)
        mark = (poll.question1_avg_mark + poll.question2_avg_mark + poll.question3_avg_mark + poll.question4_avg_mark
                + poll.question5_avg_mark)
        return mark / 5


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['first_name', 'second_name', 'patronymic', 'university', 'email', 'username']


class TeacherGetSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'second_name', 'patronymic', 'university', 'email', 'username', 'rating']

    def get_rating(self, obj):
        meetings = Meeting.objects.filter(teacher=obj.id).all()
        meeting_ids = []
        for meeting in meetings:
            meeting_ids.append(meeting.pk)

        if len(meeting_ids) == 0:
            return None
        polls = Poll.objects.filter(pk__in=meeting_ids).all()
        poll_ratings = polls.values('question1_avg_mark', 'question2_avg_mark', 'question3_avg_mark',
                                    'question4_avg_mark', 'question5_avg_mark')
        poll_ratings = list(map(lambda x: sum(x.values()) / 5, poll_ratings))
        if len(poll_ratings) == 0:
            return None
        return mean(poll_ratings)


class SearchResultSerializer(serializers.Serializer):
    subjects = serializers.ListField()
    teachers = serializers.ListField()
    universities = serializers.ListField()

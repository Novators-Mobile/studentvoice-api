from rest_framework import serializers
from .models import PollResult, Poll
from django.db.models import Sum
from admin_api.models import Meeting, Teacher, Subject


class PollSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Poll
        fields = ['id']


class PollGetSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Poll
        fields = '__all__'


def calculate_avg_mark(poll_results, question: str):
    result = poll_results.aggregate(Sum(question))
    if result[question + '__sum'] is None:
        return 0
    return result[question + '__sum']


class PollResultSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = PollResult
        fields = '__all__'

    def create(self, validated_data):
        poll = validated_data['poll']
        poll_results = PollResult.objects.filter(poll=poll)
        poll_results_count = poll_results.count() + 1

        poll_result_sum_question1 = calculate_avg_mark(poll_results, 'question1') + validated_data['question1']
        poll_result_sum_question2 = calculate_avg_mark(poll_results, 'question2') + validated_data['question2']
        poll_result_sum_question3 = calculate_avg_mark(poll_results, 'question3') + validated_data['question3']
        poll_result_sum_question4 = calculate_avg_mark(poll_results, 'question4') + validated_data['question4']
        poll_result_sum_question5 = calculate_avg_mark(poll_results, 'question5') + validated_data['question5']
        poll = Poll.objects.get(pk=poll.pk)
        poll.average_mark = (poll_result_sum_question1
                             + poll_result_sum_question2
                             + poll_result_sum_question3
                             + poll_result_sum_question4
                             + poll_result_sum_question5) / poll_results_count * 5
        poll.question1_avg_mark = poll_result_sum_question1 / poll_results_count
        poll.question2_avg_mark = poll_result_sum_question2 / poll_results_count
        poll.question3_avg_mark = poll_result_sum_question3 / poll_results_count
        poll.question4_avg_mark = poll_result_sum_question4 / poll_results_count
        poll.question5_avg_mark = poll_result_sum_question5 / poll_results_count
        poll.save()
        return PollResult.objects.create(**validated_data)


class MeetingWithTeacherGetSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = ['id', 'name', 'subject', 'date', 'poll', 'teacher', 'type', 'rating', 'teacher_name', 'subject_name']

    def get_rating(self, obj):
        poll = Poll.objects.get(pk=obj.id)
        if all([poll.question5_avg_mark, poll.question4_avg_mark, poll.question3_avg_mark, poll.question2_avg_mark, poll.question1_avg_mark]):
            mark = (poll.question1_avg_mark + poll.question2_avg_mark + poll.question3_avg_mark + poll.question4_avg_mark
                    + poll.question5_avg_mark)
            return mark / 5
        return 0

    def get_teacher_name(self, obj):
        teacher = Teacher.objects.get(pk=obj.teacher)
        return "{} {} {}".format(teacher.last_name, teacher.first_name, teacher.patronymic)

    def get_subject_name(self, obj):
        subject = Subject.objects.get(pk=obj.subject)
        return subject.name

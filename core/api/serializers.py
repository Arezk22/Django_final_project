from rest_framework import serializers
from ..models import Course, Category, Enrollment, ChatMessage


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.ReadOnlyField(source="teacher.username")

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = "__all__"


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ("id", "role", "content", "source", "created_at")
        read_only_fields = fields

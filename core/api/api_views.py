from rest_framework.authtoken.models import Token

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from .serializers import CourseSerializer, CategorySerializer, EnrollmentSerializer
from ..models import Course, Category, User, Enrollment

from .permissions import IsTeacher, IsStudent


class CoursesViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Course.objects.all()

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsTeacher]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsStudent]
    )
    def enroll(self, request, pk=None):
        course = self.get_object()

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"error": "You are already enrolled in this course"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enrollment = Enrollment.objects.create(student=request.user, course=course)

        serializer = EnrollmentSerializer(enrollment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all()


class MyEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):

        enrollments = Enrollment.objects.filter(student=request.user)

        serializer = EnrollmentSerializer(enrollments, many=True)

        return Response(serializer.data)


class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):

        courses = Course.objects.filter(teacher=request.user)

        serializer = CourseSerializer(courses, many=True)

        return Response(serializer.data)


class RegisterApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        role = request.data.get("role")

        if not username or not password or not role:
            return Response(
                {"error": "Username, password, and role are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(username=username, password=password)
        user.profile.role = role
        user.profile.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)

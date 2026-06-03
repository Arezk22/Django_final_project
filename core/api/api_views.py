from rest_framework.authtoken.models import Token

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from .serializers import (
    CourseSerializer,
    CategorySerializer,
    EnrollmentSerializer,
    ChatMessageSerializer,
    CourseDocumentSerializer,
)
from ..models import Course, Category, User, Enrollment, ChatMessage
from ..services.assistant import run_assistant

from .permissions import IsTeacher, IsStudent

from core.services.recommendation_service import get_recommendations
from ..services.assistant import run_assistant


# ==========================================
# Courses ViewSet
# ==========================================
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

    # ==========================================
    # Enroll in Course
    # ==========================================
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

    # ==========================================
    # Recommendation API (مرحلة 9)
    # ==========================================
    @action(
        detail=False, methods=["post"], permission_classes=[IsAuthenticated, IsStudent]
    )
    def recommend(self, request):

        query = request.data.get("query", "").strip()

        if not query:
            return Response(
                {"error": "query is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        recommendations = get_recommendations(request.user, query)

        return Response(recommendations, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsStudent],
    )
    def chat(self, request, pk=None):
        course = self.get_object()

        # Check enrollment
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"error": "You must be enrolled in the course to chat"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get message
        message = request.data.get("message", "").strip()

        if not message:
            return Response(
                {"error": "message is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            # Get recent messages if you store chat history in DB
            # For now, empty list like session replacement
            recent = []

            course_with_category = Course.objects.select_related("category").get(
                pk=course.pk
            )

            result = run_assistant(
                question=message,
                course=course_with_category,
                recent_messages=recent,
            )

            reply = result["content"]
            source = result.get("source", "")

            return Response(
                {
                    "message": message,
                    "reply": reply,
                    "source": source,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(e)

            return Response(
                {
                    "error": "The assistant is temporarily unavailable. Please try again."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsTeacher]
    )
    def documents(self, request, pk=None):
        course = self.get_object()

        # Ensure teacher owns this course
        if course.teacher != request.user:
            return Response(
                {"error": "You are not allowed to upload documents to this course"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CourseDocumentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(course=course)

            return Response(
                {
                    "message": "Document uploaded successfully",
                    "document": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================
# Category ViewSet
# ==========================================
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all()


# ==========================================
# My Enrollments (Student)
# ==========================================
class MyEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):

        enrollments = Enrollment.objects.filter(student=request.user)
        serializer = EnrollmentSerializer(enrollments, many=True)

        return Response(serializer.data)


# ==========================================
# My Courses (Teacher)
# ==========================================
class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):

        courses = Course.objects.filter(teacher=request.user)
        serializer = CourseSerializer(courses, many=True)

        return Response(serializer.data)


# ==========================================
# Register API
# ==========================================
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

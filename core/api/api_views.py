from rest_framework.authtoken.models import Token

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from .serializers import CourseSerializer, CategorySerializer, EnrollmentSerializer, ChatMessageSerializer
from ..models import Course, Category, User, Enrollment, ChatMessage
from ..services.assistant import run_assistant

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


class CourseChatView(APIView):
    """
    GET  /api/v1/courses/{id}/chat/  — fetch last 20 messages for this student/course
    POST /api/v1/courses/{id}/chat/  — send a message, receive AI response

    Only enrolled students may access this endpoint.
    The multi-agent pipeline (Orchestrator → RAG or General agent) runs on POST.
    """

    permission_classes = [IsAuthenticated, IsStudent]

    def _get_enrolled_course(self, request, pk):
        """Returns (course, None) or (None, error_response)."""
        try:
            course = Course.objects.select_related("category").get(pk=pk)
        except Course.DoesNotExist:
            return None, Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return None, Response(
                {"error": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return course, None

    def get(self, request, pk):
        course, err = self._get_enrolled_course(request, pk)
        if err:
            return err

        messages = ChatMessage.objects.filter(
            student=request.user, course=course
        )  # already ordered by created_at via Meta
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        course, err = self._get_enrolled_course(request, pk)
        if err:
            return err

        question = request.data.get("message", "").strip()
        if not question:
            return Response({"error": "message field is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Persist the student's message first
        ChatMessage.objects.create(
            student=request.user,
            course=course,
            role="user",
            content=question,
            source="",
        )

        # Last 10 messages (5 turns) in chronological order for context
        recent = list(
            ChatMessage.objects.filter(student=request.user, course=course)
            .order_by("-created_at")[:10]
        )[::-1] # reverse to messages order to keep chronological order


        # Run the multi-agent pipeline
        try:
            result = run_assistant(question=question, course=course, recent_messages=recent)
        except Exception as exc:
            return Response(
                {"error": f"Assistant unavailable: {str(exc)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Persist the assistant's response
        ChatMessage.objects.create(
            student=request.user,
            course=course,
            role="assistant",
            content=result["content"],
            source=result["source"],
        )

        return Response(
            {
                "role": "assistant",
                "content": result["content"],
                "source": result["source"],
                "references": result.get("references", []),
            },
            status=status.HTTP_200_OK,
        )


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

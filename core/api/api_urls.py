from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r"courses", api_views.CoursesViewSet, basename="courses")
router.register(r"categories", api_views.CategoryViewSet, basename="categories")
urlpatterns = [
    path("", include(router.urls)),
    path("my-enrollments/", api_views.MyEnrollmentsView.as_view(), name="enrollments"),
    path("my-courses/", api_views.MyCoursesView.as_view(), name="my-courses"),
    # path("courses/<int:pk>/chat/", api_views.CourseChatView.as_view(), name="course-chat"),
]

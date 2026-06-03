from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    message = (
        "You do not have permission to perform this action (Teacher role required)"
    )

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "teacher"
        )


from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    message = (
        "You do not have permission to perform this action (Student role required)"
    )

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "student"
        )

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from core.services.recommendation_service import get_recommendations
from .forms import (
    ExtendedRegistrationForm,
    CourseForm,
    CourseDocumentForm,
    UserUpdateForm,
    ProfileUpdateForm,
)
from .models import Course, Enrollment, Profile, CourseDocument, Category
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .models import Category
from core.services.recommendation_service import get_recommendations
from types import SimpleNamespace
from django.shortcuts import render
from django.db.models import Q
from .models import Course, Category, Enrollment # تأكد من صحة مسارات الاستيراد لديك
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Course, Category


# def home(request):
#     return HttpResponse('hello')


def Register(request):
    form = ExtendedRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        print(user)
        login(request, user)
        return redirect("core:course_list")
    return render(request, "core/register.html", {"form": form})



def course_list(request):
    # 1. تحديد قاعدة البيانات الأساسية للكورسات (تطبق على الكل لغرض الفلترة العامة)
    if request.user.is_authenticated and request.user.profile.role == "teacher":
        # إذا كنت تريد المدرس يرى كورساته فقط حتى عند الفلترة، اتركها كما هي.
        # ولكن بما أنك طلبت "يطبق على كل الـ courses"، سنعرض كل الكورسات أو المنشورة منها للجميع:
        courses = Course.objects.all() 
    else:
        courses = Course.objects.filter(is_published=True)

    # 2. استقبال بيانات الفلتر من الـ GET (تم تحويل search إلى query لتطابق الـ HTML)
    query = request.GET.get("query")
    category = request.GET.get("category")
    level = request.GET.get("level")

    # 3. تطبيق عمليات الفلترة
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category:
        courses = courses.filter(category__slug=category)
    if level:
        courses = courses.filter(level=level)

    # 4. حساب المعطيات الأخرى والإحصائيات (Stats)
    enrolled_ids = []

    if request.user.is_authenticated:
        role = request.user.profile.role
        if role == "teacher":
            # الإحصائيات تحسب بناءً على كورسات المدرس نفسه فقط كما كانت في كودك الأصلي
            teacher_courses = Course.objects.filter(teacher=request.user)
            stats = {
                "total": teacher_courses.count(),
                "published": teacher_courses.filter(is_published=True).count(),
                "unpublished": teacher_courses.filter(is_published=False).count(),
            }
        elif role == "student":
            enrolled_ids = Enrollment.objects.filter(student=request.user).values_list(
                "course_id", flat=True
            )
            stats = {
                "total": Course.objects.filter(is_published=True).count(),
                "published": Course.objects.filter(is_published=True).count(),
                "enrolled": len(enrolled_ids),
            }
        elif role == "admin":
            stats = {
                "total": Course.objects.count(),
                "published": Course.objects.filter(is_published=True).count(),
                "unpublished": Course.objects.filter(is_published=False).count(),
            }
    else:
        stats = {
            "total": Course.objects.filter(is_published=True).count(),
            "published": Course.objects.filter(is_published=True).count(),
            "unpublished": 0,
        }

    filtered_courses_count = courses.count()

    # 5. تمرير القيم إلى الـ Context
    context = {
        "course": courses,
        "filtered_courses_count": filtered_courses_count,
        "categories": Category.objects.all(),
        "enrolled_ids": enrolled_ids,
        "stats": stats,
        # أضفنا هذه المتغيرات لكي يقرأها الـ Template ويحافظ على الكلمات المختارة داخل حقول الفلتر
        "query": query,
        "category": category,
        "level": level,
    }
    return render(request, "core/course_list.html", context)


@login_required
def create_course(request):
    if not request.user.is_active:
        raise PermissionDenied
    if request.user.profile.role != "teacher":
        raise PermissionDenied
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect("core:course_list")
    else:
        form = CourseForm()
    return render(request, "core/course_form.html", {"form": form, "action": "create"})


@login_required
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not request.user.is_active:
        raise PermissionDenied
    if request.user.profile.role != "teacher":
        raise PermissionDenied
    if course.teacher != request.user:
        raise PermissionDenied

    if request.method == "POST":

        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("core:course_list")
    else:
        form = CourseForm(instance=course)
    return render(request, "core/course_form.html", {"form": form, "action": "update"})


@login_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not request.user.is_active:
        raise PermissionDenied

    if request.user.profile.role != "teacher":
        raise PermissionDenied
    if course.teacher != request.user:
        raise PermissionDenied

    if request.method == "POST":
        course.delete()
        return redirect("core:course_list")

    return render(request, "core/course_confirm_delete.html", {"course": course})


def course_details(request, pk):
    course = get_object_or_404(Course, pk=pk)

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()
    return render(
        request,
        "core/course_details.html",
        {"course": course, "is_enrolled": is_enrolled},
    )


@login_required
def enroll_course(request, course_id):

    if request.user.profile.role != "student":
        raise PermissionDenied

    course = get_object_or_404(Course, id=course_id, is_published=True)

    if request.method == "POST":
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, course=course
        )
        if created:
            messages.success(
                request, f"Enrollment successful! Welcome to {course.title}."
            )
        else:
            messages.warning(request, f"You are already enrolled in {course.title}.")

        return redirect("core:course_details", pk=course_id)

    return HttpResponse("Invalid request", status=400)


@login_required
def myenrollments(request):
    try:
        if request.user.profile.role != "student":
            raise PermissionDenied("You do not have permission to view this page.")
    except Profile.DoesNotExist:
        raise PermissionDenied("Profile not found.")

    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, "core/my_enrollments.html", {"enrollments": enrollments})


@login_required
def mycourses(request):
    try:
        if request.user.profile.role != "teacher":
            raise PermissionDenied("You do not have permission to view this page.")
    except AttributeError:
        raise PermissionDenied("Profile not found.")

    created_courses = Course.objects.filter(teacher=request.user).order_by("-id")

    context = {
        "courses": created_courses,
    }

    return render(request, "core/mycourse.html", context)


@login_required
def document_upload(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.user.profile.role != "teacher":
        raise PermissionDenied
    if course.teacher != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = CourseDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.course = course
            doc.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect("core:document_upload", pk=pk)
    else:
        form = CourseDocumentForm()
    docs = CourseDocument.objects.filter(course=course)
    return render(
        request,
        "core/document_upload.html",
        {"course": course, "form": form, "docs": docs},
    )


@login_required
def all_documents_view(request):

    documents = CourseDocument.objects.all()
    return render(request, "core/all_documents.html", {"documents": documents})


@login_required
def course_assistant(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)

    if request.user.profile.role != "student":
        raise PermissionDenied
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        raise PermissionDenied

    session_key = f"chat_{request.user.id}_{course.pk}"

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if message:
            history = request.session.get(session_key, [])

            # Pass the last 10 session messages as context (before the current question)
            recent = [
                SimpleNamespace(role=m["role"], content=m["content"])
                for m in history[-10:]
            ]

            try:
                from .services.assistant import run_assistant

                course_with_category = Course.objects.select_related("category").get(
                    pk=pk
                )
                result = run_assistant(
                    question=message,
                    course=course_with_category,
                    recent_messages=recent,
                )
                reply = result["content"]
                source = result.get("source", "")
            except Exception as e:
                print(e)
                reply = "The assistant is temporarily unavailable. Please try again."
                source = ""

            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": reply, "source": source})
            request.session[session_key] = history

        return redirect("core:course_assistant", pk=pk)

    chat_history = request.session.get(session_key, [])
    return render(
        request,
        "core/course_assistant.html",
        {"course": course, "chat_history": chat_history},
    )


@login_required
def clear_chat(request, pk):
    if request.method == "POST":
        session_key = f"chat_{request.user.id}_{pk}"
        request.session.pop(session_key, None)
    return redirect("core:course_assistant", pk=pk)


# --------------------profile view------------------#
@login_required
def profile_view(request):
    if request.method == "POST":

        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("core:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}
    return render(request, "core/profile.html", context)


######################
# RECOMMENDATION VIEW
#####################



# تأكد من استيراد دالة الذكاء الاصطناعي لديك
# from .utils import get_recommendations 

@login_required
def recommend(request):
    # إذا كان الطلب قادم من الـ Chatbot عبر JavaScript (AJAX)
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()
            
            if not user_message:
                return JsonResponse({"status": "error", "message": "Empty message"}, status=400)
            
            # 1. جلب معلومات كل الكورسات من قاعدة البيانات وتلخيصها للـ AI
            all_courses = Course.objects.all() # أو filter(is_published=True) حسب رغبتك
            courses_context = "Available Courses in Database:\n"
            for c in all_courses:
                courses_context += f"- Title: {c.title} | Category: {c.category} | Level: {c.level} | Description: {c.description[:150]}...\n"
            
            # 2. دمج سياق الكورسات مع سؤال المستخدم لتوجيه الـ AI
            prompt_for_ai = (
                f"You are a helpful Career Advisor AI inside an educational platform.\n"
                f"{courses_context}\n"
                f"User Question: {user_message}\n"
                f"Answer the user query accurately based ONLY on the available courses listed above if they are asking about courses. Be concise and friendly."
            )
            
            # 3. إرسال الـ prompt المعدل لدالة الذكاء الاصطناعي (تأكد أن دالتك تقبل نص الـ prompt)
            ai_response = get_recommendations(request.user, prompt_for_ai)
            
            return JsonResponse({
                "status": "success",
                "reply": ai_response
            })
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # -------------------------------------------------------------
    # الجزء القديم الخاص بصفحة التوصيات العادية (Form Submit)
    # -------------------------------------------------------------
    recommendations = []
    query = ""
    category = ""
    level = ""

    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        category = request.POST.get("category", "").strip()
        level = request.POST.get("level", "").strip()

        parts = [query]
        if category: parts.append(f"category {category}")
        if level: parts.append(f"level {level}")

        search_query = " ".join(parts)
        recommendations = get_recommendations(request.user, search_query)

    return render(
        request,
        "core/course_list.html",
        {
            "recommendations": recommendations,
            "categories": Category.objects.all(),
            "query": query,
            "category": category,
            "level": level,
        },
    )
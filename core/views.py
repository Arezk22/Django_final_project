from django.shortcuts import render
from .models import Category
from core.services.recommendation_service import get_recommendations
from types import SimpleNamespace

# def home(request):
#     return HttpResponse('hello')


def Register(request):
    form = ExtendedRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        print(user)
        login(request, user)
        return redirect('core:course_list')
    return render(request, 'core/register.html', {'form': form})


def course_list(request):
    if request.user.is_authenticated and request.user.profile.role == 'teacher':
        courses = Course.objects.filter(teacher=request.user)
    else:
        courses = Course.objects.filter(is_published=True)
   
    search = request.GET.get('search')
    category = request.GET.get('category')
    level = request.GET.get('level')

    if search:
        courses = courses.filter(title__icontains=search) | \
                  courses.filter(description__icontains=search)
    if category:
        courses = courses.filter(category__slug=category)
    if level:
        courses = courses.filter(level=level)

    enrolled_ids = []
    
    if request.user.is_authenticated:
        role = request.user.profile.role
        if role == 'teacher':
            stats = {
                'total': courses.count(),
                'published': courses.filter(is_published=True).count(),   
                'unpublished': courses.filter(is_published=False).count(),  
            }
        elif role == 'student':
            enrolled_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
            stats = {
                'total': Course.objects.filter(is_published=True).count(),
                'published': Course.objects.filter(is_published=True).count(),      
                'enrolled': len(enrolled_ids),                                    
            }
        elif role == 'admin':
            stats = {
                'total': Course.objects.count(),
                'published': Course.objects.filter(is_published=True).count(),      
                'unpublished': Course.objects.filter(is_published=False).count(),  
            }
    else:
        stats = {
            'total': Course.objects.filter(is_published=True).count(),
            'published': Course.objects.filter(is_published=True).count(),
            'unpublished': 0
        }

    filtered_courses_count = courses.count()

    context = {
        'course': courses,
        'filtered_courses_count': filtered_courses_count,
        'categories': Category.objects.all(),
        'enrolled_ids': enrolled_ids,
        'stats': stats,  
    }
    return render(request, 'core/course_list.html', context)

@login_required
def create_course(request):
    if not request.user.is_active:
        raise PermissionDenied
    if request.user.profile.role != 'teacher':
        raise PermissionDenied
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('core:course_list')
    else:
        form = CourseForm()
    return render(request, 'core/course_form.html', {'form': form, 'action': 'create'})



@login_required
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not request.user.is_active:
        raise PermissionDenied
    if request.user.profile.role != 'teacher':
        raise PermissionDenied
    if course.teacher != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('core:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'core/course_form.html', {'form': form, 'action': 'update'})



@login_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not request.user.is_active:
        raise PermissionDenied

    if request.user.profile.role != 'teacher':
        raise PermissionDenied
    if course.teacher != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        course.delete()
        return redirect('core:course_list')

    return render(request, 'core/course_confirm_delete.html', {'course': course})

def course_details(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()
    return render(request, 'core/course_details.html', { 'course': course,  'is_enrolled': is_enrolled})


@login_required
def enroll_course(request, course_id):
   
    if request.user.profile.role != 'student':
        raise PermissionDenied

    course = get_object_or_404(Course, id=course_id, is_published=True)

    if request.method == 'POST':
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )
        if created:
            messages.success(request, f'Enrollment successful! Welcome to {course.title}.')
        else:
            messages.warning(request, f'You are already enrolled in {course.title}.')

        return redirect('core:course_details', pk=course_id)

    return HttpResponse('Invalid request', status=400)


@login_required
def myenrollments(request):
    try:
        if request.user.profile.role != 'student':
            raise PermissionDenied("You do not have permission to view this page.")
    except Profile.DoesNotExist:
        raise PermissionDenied("Profile not found.")

    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'core/my_enrollments.html', {'enrollments': enrollments})


@login_required
def mycourses(request):
    try:
        if request.user.profile.role != 'teacher':
            raise PermissionDenied("You do not have permission to view this page.")
    except AttributeError:
        raise PermissionDenied("Profile not found.")

    created_courses = Course.objects.filter(teacher=request.user).order_by('-id')

    context = {
        'courses': created_courses, 
    }
    
    return render(request, 'core/mycourse.html', context)



@login_required
def document_upload(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.user.profile.role != 'teacher':
        raise PermissionDenied
    if course.teacher != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = CourseDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.course = course
            doc.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('core:document_upload', pk=pk)
    else:
        form = CourseDocumentForm()
    docs = CourseDocument.objects.filter(course=course)
    return render(request, 'core/document_upload.html', {'course': course, 'form': form, 'docs': docs})

@login_required
def all_documents_view(request):
 
    documents = CourseDocument.objects.all()
    return render(request, 'core/all_documents.html', {
        'documents': documents
    })

@login_required
def course_assistant(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)

    if request.user.profile.role != 'student':
        raise PermissionDenied
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        raise PermissionDenied

    session_key = f'chat_{request.user.id}_{course.pk}'

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            history = request.session.get(session_key, [])

            # Pass the last 10 session messages as context (before the current question)
            recent = [
                SimpleNamespace(role=m['role'], content=m['content'])
                for m in history[-10:]
            ]

            try:
                from .services.assistant import run_assistant
                course_with_category = Course.objects.select_related('category').get(pk=pk)
                result = run_assistant(
                    question=message,
                    course=course_with_category,
                    recent_messages=recent,
                )
                reply = result['content']
                source = result.get('source', '')
            except Exception:
                reply = 'The assistant is temporarily unavailable. Please try again.'
                source = ''

            history.append({'role': 'user', 'content': message})
            history.append({'role': 'assistant', 'content': reply, 'source': source})
            request.session[session_key] = history

        return redirect('core:course_assistant', pk=pk)

    chat_history = request.session.get(session_key, [])
    return render(request, 'core/course_assistant.html', {'course': course,'chat_history': chat_history })


@login_required
def clear_chat(request, pk):
    if request.method == 'POST':
        session_key = f'chat_{request.user.id}_{pk}'
        request.session.pop(session_key, None)
    return redirect('core:course_assistant', pk=pk)



#--------------------profile view------------------#
@login_required
def profile_view(request):
    if request.method == 'POST':
        
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('core:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'core/profile.html', context)


######################
# RECOMMENDATION VIEW 
#####################


@login_required 
def recommend(request):
    recommendations = []

    query = ""
    category = ""
    level = ""

    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        category = request.POST.get("category", "").strip()
        level = request.POST.get("level", "").strip()

        parts = [query]

        if category:
            parts.append(f"category {category}")

        if level:
            parts.append(f"level {level}")

        search_query = " ".join(parts)

        recommendations = get_recommendations(
            request.user,
            search_query
        )

    return render(
        request,
        "courses/recommend.html",
        {
            "recommendations": recommendations,
            "categories": Category.objects.all(),
            "query": query,
            "category": category,
            "level": level,
        }
    )
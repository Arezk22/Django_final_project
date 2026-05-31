from django.urls import path,include
from . import views
app_name='core'

urlpatterns =[
    # path('home/',views.home,name='home'),
    path('',views.course_list,name='course_list'),
    path('course/create/',views.create_course,name='create_course'),
    path('course/update/<int:pk>/',views.update_course,name='update_course'),
    path('course/delete/<int:pk>/',views.delete_course,name='delete_course'),
   path('course/details/<int:pk>/',views.course_details,name='course_details'),
   path('enroll_course/<int:course_id>/enroll',views.enroll_course,name='enroll_course'),
   path('myenrollments/',views.myenrollments,name='my_enrollments'),
   path('mycourses/',views.mycourses,name='my_courses'),
   path('course/<int:pk>/documents/', views.document_upload, name='document_upload'),
   path('course/<int:pk>/assistant/', views.course_assistant, name='course_assistant'),
   path('courses/<int:pk>/assistant/clear/', views.clear_chat, name='clear_chat'),
   path('documents/', views.all_documents_view, name='all_documents'),
   path('profile/', views.profile_view, name='profile'),
]
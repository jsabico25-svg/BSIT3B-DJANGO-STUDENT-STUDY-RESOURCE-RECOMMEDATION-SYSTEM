from django.urls import path

from . import views

app_name = 'student_subjects'

urlpatterns = [
    path('', views.enrollment_list_page, name='enrollment_list'),
    path(
        'ajax/save/',
        views.enrollment_save_ajax,
        name='enrollment_save_ajax',
    ),
    path(
        'ajax/delete/<int:pk>/',
        views.enrollment_delete_ajax,
        name='enrollment_delete_ajax',
    ),
]

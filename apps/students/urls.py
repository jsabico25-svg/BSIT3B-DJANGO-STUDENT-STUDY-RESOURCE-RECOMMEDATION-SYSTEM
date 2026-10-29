from django.urls import path

from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list_page, name='student_list'),
    path('ajax/save/', views.student_save_ajax, name='student_save_ajax'),
    path(
        'ajax/delete/<int:pk>/',
        views.student_delete_ajax,
        name='student_delete_ajax',
    ),
]

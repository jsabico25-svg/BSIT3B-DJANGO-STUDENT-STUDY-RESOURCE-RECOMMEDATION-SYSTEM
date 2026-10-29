from django.urls import path

from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_list_page, name='feedback_list'),
    path('ajax/save/', views.feedback_save_ajax, name='feedback_save_ajax'),
    path(
        'ajax/delete/<int:pk>/',
        views.feedback_delete_ajax,
        name='feedback_delete_ajax',
    ),
]

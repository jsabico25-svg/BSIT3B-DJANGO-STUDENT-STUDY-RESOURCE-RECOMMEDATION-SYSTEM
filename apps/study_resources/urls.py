from django.urls import path

from . import views

app_name = 'study_resources'

urlpatterns = [
    path('', views.resource_list_page, name='resource_list'),
    path('ajax/save/', views.resource_save_ajax, name='resource_save_ajax'),
    path(
        'ajax/delete/<int:pk>/',
        views.resource_delete_ajax,
        name='resource_delete_ajax',
    ),
]

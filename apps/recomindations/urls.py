from django.urls import path

from . import views

app_name = 'recomindations'

urlpatterns = [
    path('', views.recommendation_list_page, name='recommendation_list'),
    path(
        'ajax/save/',
        views.recommendation_save_ajax,
        name='recommendation_save_ajax',
    ),
    path(
        'ajax/delete/<int:pk>/',
        views.recommendation_delete_ajax,
        name='recommendation_delete_ajax',
    ),
    path(
        'ajax/generate/<int:student_pk>/',
        views.recommendation_generate_ajax,
        name='recommendation_generate_ajax',
    ),
    path(
        'ajax/generate-all/',
        views.recommendation_generate_all_ajax,
        name='recommendation_generate_all_ajax',
    ),
]

from django.urls import path
from .views import event_list_view, event_category_list_view,event_detail_view

urlpatterns = [
    path('', event_list_view, name='event-list'),
    path('categories/', event_category_list_view, name='event-category-list'),
     path('<int:pk>/', event_detail_view, name='event-detail'),
]
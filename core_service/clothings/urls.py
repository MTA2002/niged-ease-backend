from django.urls import path
from clothings.views import (
    CollectionListView,
    CollectionDetailView,
    ColorListView,
    ColorDetailView,
    SeasonListView,
    SeasonDetailView
)

urlpatterns = [
    # Color URLs
    path('colors/', ColorListView.as_view(), name='color-list'),
    path('colors/<uuid:id>/', ColorDetailView.as_view(), name='color-detail'),
    
    # Season URLs
    path('seasons/', SeasonListView.as_view(), name='season-list'),
    path('seasons/<uuid:id>/', SeasonDetailView.as_view(), name='season-detail'),

    # Collection URLs
    path('collections/', CollectionListView.as_view(), name='collection-list'),
    path('collections/<uuid:id>/', CollectionDetailView.as_view(), name='collection-detail'),
] 
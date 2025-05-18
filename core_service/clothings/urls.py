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
    path('stores/<uuid:store_id>/colors/', ColorListView.as_view(), name='color-list'),
    path('stores/<uuid:store_id>/colors/<uuid:id>/', ColorDetailView.as_view(), name='color-detail'),
    
    # Season URLs
    path('stores/<uuid:store_id>/seasons/', SeasonListView.as_view(), name='season-list'),
    path('stores/<uuid:store_id>/seasons/<uuid:id>/', SeasonDetailView.as_view(), name='season-detail'),

    # Collection URLs
    path('stores/<uuid:store_id>/collections/', CollectionListView.as_view(), name='collection-list'),
    path('stores/<uuid:store_id>/collections/<uuid:id>/', CollectionDetailView.as_view(), name='collection-detail'),
] 
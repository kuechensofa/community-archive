from django.urls import path
from django.shortcuts import redirect

from archive import views, api

urlpatterns = [
    path('', lambda req: redirect('/collections/')),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),
    path('collections/', views.CollectionListView.as_view(), name='collection-list'),
    path('collections/<int:pk>/', views.CollectionDetailView.as_view(), name='collection-detail'),
    path('collections/add/', views.CollectionCreateView.as_view(), name='collection-create'),
    path('collections/<int:pk>/edit/', views.CollectionUpdateView.as_view(), name='collection-update'),
    path('collections/<int:pk>/delete/', views.CollectionDeleteView.as_view(), name='collection-delete'),
    path('collections/<int:collection_id>/records/add/', views.RecordCreateView.as_view(), name='record-create'),
    path('collections/<int:collection_id>/records/<int:pk>/', views.RecordDetailView.as_view(), name='record-detail'),
    path('collections/<int:collection_id>/records/<int:pk>/add-tag/', views.add_tag_view, name='record-add-tag'),
    path('collections/<int:collection_id>/records/<int:pk>/edit/', views.RecordUpdateView.as_view(),
         name='record-update'),
    path('collections/<int:collection_id>/records/<int:pk>/delete/', views.RecordDeleteView.as_view(),
         name='record-delete'),
    path('collections/<int:collection_id>/records/<int:record_id>/files/', views.upload_record_file,
         name='record-files-add'),
    path('collections/<int:collection_id>/records/<int:record_id>/files/<int:pk>/delete/',
         views.RecordFileDeleteView.as_view(), name='record-files-delete'),
    path('search/', views.search_view, name='search'),
    path('tags/add/', views.RecordTagCreateView.as_view(), name='tag-create'),
    path('tags/autocomplete/', api.tag_autocomplete, name='tag-autocomplete'),
]

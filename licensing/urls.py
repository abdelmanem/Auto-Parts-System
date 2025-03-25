from django.urls import path
from . import views

app_name = 'licensing'

urlpatterns = [
    path('licenses/', views.LicenseListView.as_view(), name='license_list'),
    path('licenses/create/', views.LicenseCreateView.as_view(), name='license_create'),
    path('licenses/<int:pk>/update/', views.LicenseUpdateView.as_view(), name='license_update'),
    path('licenses/<int:pk>/delete/', views.LicenseDeleteView.as_view(), name='license_delete'),
    path('licenses/<int:pk>/', views.LicenseDetailView.as_view(), name='license_detail'),
]
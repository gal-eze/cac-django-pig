from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update-prices', views.update_values, name="update-prices"),

    path('transactions/', views.transaction_list, name='transaction-list'),
    path('transactions/filter/', views.transaction_filter, name='transaction-filter'),
    path('transactions/create/', views.transaction_create, name='transaction-create'),
    path('transactions/<int:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction-update'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction-delete'),
    
    path('upload/', views.upload_file, name='upload-file'),
    path('preview/', views.preview_data, name='preview-data'),
    path('save/', views.save_data, name='save-data'),
    
    path('securities/', views.securities_list, name='security-list'),
    path('securities/filter/', views.security_filter, name='security-filter'),

    path('page-user/', views.page_user, name='page-user'),
]

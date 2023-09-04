from django.urls import path
from . import views
from .views import index, signup_view, login_view, logout_view, profile_view, dashboard, upload_dataset_view, perform_anomaly_detection, \
    data_summary_view

urlpatterns = [
    path('', index, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile-update/', profile_view, name='update_profile'),
    path('upload/', upload_dataset_view, name='upload'),
    path('data_summary/<int:dataset_id>/', data_summary_view, name='data_summary'),
    path('perform_anomaly_detection/', perform_anomaly_detection, name='perform_anomaly_detection'),
    #path('convert/<int:file_id>/', convert_file_view, name='convert'),
    #path('save/<int:file_id>/', save_file_view, name='save'),
    #path('my-files/', file_list_view, name='file_list'),
]

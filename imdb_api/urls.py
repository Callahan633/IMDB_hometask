from django.contrib import admin
from django.urls import path, re_path, include

from api.views import CreateTaskAPIView, GetTaskAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'^api/create_task/?$', CreateTaskAPIView.as_view(), name='Create search task'),
    re_path(r'^api/get_task/?$', GetTaskAPIView.as_view({'post': 'retrieve'}), name='Get existing task')
]

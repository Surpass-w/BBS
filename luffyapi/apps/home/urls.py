from django.urls import path, re_path
from . import views

urlpatterns = [
    path('banner/', views.BannerView.as_view(actions={'get': 'list'})),
]

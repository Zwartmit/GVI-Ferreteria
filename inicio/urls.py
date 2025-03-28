from django.urls import path
from inicio.views import *

urlpatterns = [
    path('', indexView.as_view(), name='index')
]

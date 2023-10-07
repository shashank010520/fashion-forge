from django.urls import path
from home.views import *

urlpatterns = [
   path('' , index , name="index"),
   path('home' , home , name="home"),
   path('my-account' , profile , name="profile"),
   path('contact' , contact , name="contact"),
   path('about' , about , name="about"),
]
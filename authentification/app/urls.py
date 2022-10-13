from unicodedata import name
from django.urls import path
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),

]

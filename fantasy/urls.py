from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('my-squad/', views.my_squad, name='my_squad'),
    path('stats/', views.stats, name='stats'),
    path('value-picks/', views.value_picks, name='value_picks'),
    path('best-xi/', views.best_xi, name='best_xi'),

]

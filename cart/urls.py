from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='cart.index'),
    path('<int:id>/add/', views.add, name='cart.add'),
    path('clear/', views.clear, name='cart.clear'),
    path('purchase/', views.purchase, name='cart.purchase'),
    path('toppurchases/', views.top_purchases, name='cart.top_purchases'), 
    path('subscriptionlevel/', views.subscription_level, name='cart.subscription_level')
]
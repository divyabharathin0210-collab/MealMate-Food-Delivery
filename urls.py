from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index),
    path('open_signin', views.open_signin, name='open_signin'),
    path('open_signup', views.open_signup, name='open_signup'),
    path('login', views.signin, name='login'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('customer_home/', views.customer_home, name='customer_home'),
    path('open_add_restaurant', views.open_add_restaurant, name='open_add_restaurant'), 
    path('add_restaurant', views.add_restaurant, name='add_restaurant'),
    path('open_show_restaurant', views.open_show_restaurant, name='open_show_restaurant'), 
    path('open_update_restaurant/<int:restaurant_id>', views.open_update_restaurant, name='open_update_restaurant'), 
    path('update_restaurant/<int:restaurant_id>', views.update_restaurant, name='update_restaurant'), 
    path('delete_restaurant/<int:restaurant_id>', views.delete_restaurant, name='delete_restaurant'), 
    path('open_update_menu/<int:restaurant_id>', views.open_update_menu, name='open_update_menu'), 
    path('update_menu/<int:restaurant_id>', views.update_menu, name='update_menu'),
    path('view_menu/<int:restaurant_id>/u/', views.view_menu, name='view_menu'), 

    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase_qty/<int:item_id>/', views.increase_qty, name='increase_qty'),
    path('decrease_qty/<int:item_id>/', views.decrease_qty, name='decrease_qty'),
    path('show_cart/', views.show_cart, name='show_cart'), 

    path('checkout/', views.checkout, name='checkout'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('orders/', views.orders, name='orders'),
    path('order_history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('search/', views.search, name='search'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
]





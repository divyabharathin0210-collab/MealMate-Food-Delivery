from django.contrib import admin

from .models import Customer, Restaurant, Item, Order, OrderItem
# Register your models here.
admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)
# admin.site.register(Cart)
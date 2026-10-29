from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Customer, Restaurant, Item, Order, OrderItem, PasswordResetOTP
from django.contrib.auth.models import User
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # ← This was missing
from django.db import transaction
 # change Restaurant to your actual model name
import re
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import random
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



def customer_home(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/customer_home.html', {
        'restaurantList': restaurantList,
        'user': request.user
    })


# Create your views here.
def index(request):
    return render(request, 'delivery/index.html')

def open_signin(request):
    return render(request, 'delivery/signin.html')

def open_signup(request):
    return render(request, 'delivery/signup.html')


from django.contrib.auth.password_validation import validate_password


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']

        # 1. Check username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Try another one.")
            return render(request, 'delivery/signup.html')

        # 2. Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return render(request, 'delivery/signup.html')

        # 3. Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'delivery/signup.html')

        # 4. Validate mobile: 10 digits only
        if not re.match(r'^\d{10}$', mobile):
            messages.error(request, "Mobile must be exactly 10 digits.")
            return render(request, 'delivery/signup.html')

        # 5. Check if mobile exists
        if Customer.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return render(request, 'delivery/signup.html')

        # 6. Validate password using Django validators from settings.py
        try:
            validate_password(password, user=User(username=username, email=email))
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return render(request, 'delivery/signup.html')
    
        # 7. Create user and customer - only if all checks pass
        user = User.objects.create_user(username=username, email=email, password=password)
        Customer.objects.create(user=user, mobile=mobile, address=address)
        messages.success(request, "Account created! Login now.")
        return redirect('signin')
    
    return render(request, 'delivery/signup.html')

def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            if user.is_staff:  # this works
                return redirect('/admin/')
            else:
                return redirect('customer_home')
        else:
            return render(request, 'delivery/signin.html', {'error': 'Invalid credentials'})
    
    return render(request, 'delivery/signin.html')    
   

def open_add_restaurant(request):
    return render(request, 'delivery/add_restaurant.html')

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        try:
            Restaurant.objects.get(name = name)
            return HttpResponse("Duplicate restaurant!")
        except:
            Restaurant.objects.create(
                name = name,
                picture = picture,
                cuisine = cuisine,
                rating = rating,
            )
    return render(request, 'delivery/admin_home.html')

def open_show_restaurant(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})

def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'delivery/update_restaurant.html', {"restaurant" : restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        
        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating

        restaurant.save()
       
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})


def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html',{"restaurantList" : restaurantList})


def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #itemList = Item.objects.all()
    return render(request, 'delivery/update_menu.html',{"itemList" : itemList, "restaurant" : restaurant})
    
def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = request.POST.get('vegeterian') == 'on'
        picture = request.POST.get('picture')
        
        try:
            Item.objects.get(name = name)
            return HttpResponse("Duplicate item!")
        except:
            Item.objects.create(
                restaurant = restaurant,
                name = name,
                description = description,
                price = price,
                vegeterian = vegeterian,
                picture = picture,
            )
    return render(request, 'delivery/admin_home.html')

def view_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)
    itemList = restaurant.items.all()
    
    cart = request.session.get('cart', {})
    print("SESSION CART:", cart)  # <-- Add this line
    cart_items = {int(key): value for key, value in cart.items()}
    
    return render(request, 'delivery/customer_menu.html', {
        "itemList": itemList,
        "restaurant": restaurant,
        "cart_items": cart_items
    })
def add_to_cart(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    cart[item_id] = cart.get(item_id, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    
    item = Item.objects.get(id=item_id)
    return redirect('view_menu', restaurant_id=item.restaurant.id)


def increase_qty(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    
    if item_id in cart:
        cart[item_id] += 1
        request.session['cart'] = cart
        request.session.modified = True
    
    item = Item.objects.get(id=item_id)
    return redirect('view_menu', restaurant_id=item.restaurant.id)


def decrease_qty(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)
    
    if item_id in cart:
        if cart[item_id] > 1:
            cart[item_id] -= 1
        else:
            del cart[item_id]  # remove if qty becomes 0
        request.session['cart'] = cart
        request.session.modified = True
    
    item = Item.objects.get(id=item_id)
    return redirect('view_menu', restaurant_id=item.restaurant.id)


def show_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total_price = 0
    
    for item_id, qty in cart.items():
        item = Item.objects.get(id=int(item_id))
        items.append({'item': item, 'quantity': qty, 'subtotal': item.price * qty})
        total_price += item.price * qty
    
    return render(request, 'delivery/cart.html', {
        "itemList": items, 
        "total_price": total_price
    })
# Checkout View
# Checkout View
import razorpay

def checkout(request):
    if not request.user.is_authenticated:  # RIGHT - uses Django auth
        return redirect('signin')
    
    cart = request.session.get('cart', {})
    if not cart:
        return render(request, 'delivery/checkout.html', {'error': 'Cart is empty'})
    
    itemList = []
    subtotal = 0
    
    for item_id, qty in cart.items():
        try:
            item = Item.objects.get(id=item_id)
            item_subtotal = item.price * qty
            subtotal += item_subtotal
            itemList.append({
                'item': item,
                'quantity': qty,
                'subtotal': item_subtotal
            })
        except Item.DoesNotExist:
            pass
    
    delivery_fee = 40
    total_price = subtotal + delivery_fee
    
    context = {
        'itemList': itemList,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total_price': total_price,
        'amount_paise': int(total_price * 100),
        'username': request.user.username  # Use request.user here
    }
    return render(request, 'delivery/checkout.html', context)
 
@login_required(login_url='signin')
@transaction.atomic
def orders(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('customer_home')
    
    customer = Customer.objects.get(user=request.user)
    
    # Calculate total and build items list
    items = []
    total_amount = 0
    for item_id, qty in cart.items():
        try:
            item = Item.objects.get(id=int(item_id))
            subtotal = item.price * qty
            items.append({
                'item': item, 
                'quantity': qty, 
                'price': item.price,
                'subtotal': subtotal
            })
            total_amount += subtotal
        except Item.DoesNotExist:
            continue
    
    if not items:
        return redirect('customer_home')
    
    # THIS PART SAVES TO DATABASE - you probably don't have it yet
    order = Order.objects.create(
        customer=customer,
        total_amount=total_amount,
        address=customer.address
    )
    
    for item_data in items:
        OrderItem.objects.create(
            order=order,
            item=item_data['item'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
    
    # Clear cart AFTER saving
    request.session['cart'] = {}
    request.session.modified = True
    
    context = {
        'username': request.user.username,
        'address': customer.address,
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'delivery/orders.html', context)

@login_required(login_url='signin')
def order_history(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect('customer_home')
    
    orders = Order.objects.filter(customer=customer).order_by('-created_at').prefetch_related('items__item')
    
    context = {
        'orders': orders,
        'username': request.user.username,
    }
    return render(request, 'delivery/order_history.html', context)

@login_required(login_url='signin')
def order_detail(request, order_id):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect('customer_home')
    
    # Only allow user to see their own orders
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    context = {
        'order': order,
        'order_items': order.items.select_related('item__restaurant')
    }
    return render(request, 'delivery/order_detail.html', context)


@login_required(login_url='signin')
def search(request):
    query = request.GET.get('q', '').strip()
    restaurants = []
    items = []
    
    if query:
        restaurants = Restaurant.objects.filter(
            Q(name__icontains=query) | Q(cuisine__icontains=query)
        )
        items = Item.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).select_related('restaurant')[:10]
    
    context = {
        'query': query,
        'restaurants': restaurants,
        'items': items,
        'result_count': len(restaurants) + len(items)
    }
    return render(request, 'delivery/search.html', context)

@csrf_exempt
def chatbot(request):
    if request.method!= 'POST':
        return JsonResponse({'error': 'POST only'})

    data = json.loads(request.body)
    user_msg = data.get('message', '').lower().strip()
    words = user_msg.split()

    # Default reply
    reply = "I'm MealMate Bot 🤖 Ask me: 'recommend food', 'veg under 200', 'pizza', 'best rated'"

    # 1. Greeting - EXACT match only
    if user_msg in ['hi', 'hello', 'hey', 'help', 'hi!', 'hello!']:
        reply = "Hey! I can help you find food 🍕\nTry:\n• 'recommend something'\n• 'veg under 300'\n• 'spicy'\n• 'pizza'"

    # 2. Recommendations
    elif 'recommend' in user_msg or 'suggest' in user_msg:
        items = list(Item.objects.all().order_by('?')[:3])
        if items:
            reply = "Try these: "
            for item in items:
                reply += f"\n• {item.name} from {item.restaurant.name} - ₹{int(item.price)}"
        else:
            reply = "No items in database yet. Add some in Django admin!"

    # 3. COMBINED PRICE + VEG/NON-VEG FILTER - FIXED ORDER
    elif 'under' in user_msg or 'below' in user_msg:
        numbers = re.findall(r'\d+', user_msg) # FIXED: was r.findall
        if numbers:
            price_limit = int(numbers[0])
            items = Item.objects.filter(price__lte=price_limit)

            # Check for veg/non-veg in same query
            if 'veg' in user_msg and 'non' not in user_msg:
                items = items.filter(vegetarian=True)
                prefix = "veg "
            elif 'non-veg' in user_msg or 'nonveg' in user_msg or 'chicken' in user_msg:
                items = items.filter(vegetarian=False)
                prefix = "non-veg "
            else:
                prefix = ""

            items = items.order_by('price')[:3]

            if items:
                reply = f"Top {prefix}picks under ₹{price_limit}:"
                for item in items:
                    reply += f"\n• {item.name} - ₹{int(item.price)} at {item.restaurant.name}"
            else:
                reply = f"No {prefix}items found under ₹{price_limit} 😔"

    # 4. Veg filter - only runs if 'under' not in message
    elif 'veg' in user_msg and 'non' not in user_msg:
        items = Item.objects.filter(vegetarian=True).order_by('?')[:3]
        if items:
            reply = "Top veg picks: "
            for item in items:
                reply += f"\n• {item.name} - ₹{int(item.price)} at {item.restaurant.name}"
        else:
            reply = "No veg items found."

    # 5. Non-veg filter
    elif 'non-veg' in user_msg or 'nonveg' in user_msg or 'chicken' in user_msg:
        items = Item.objects.filter(vegetarian=False).order_by('?')[:3]
        if items:
            reply = "Top non-veg picks: "
            for item in items:
                reply += f"\n• {item.name} - ₹{int(item.price)} at {item.restaurant.name}"
        else:
            reply = "No non-veg items found."

    # 6. Spicy search
    elif 'spicy' in user_msg or 'hot' in user_msg:
        items = Item.objects.filter(
            Q(name__icontains='spicy') | Q(name__icontains='chilli') |
            Q(name__icontains='masala') | Q(description__icontains='spicy')
        )[:3]
        if items:
            reply = "Spicy options: "
            for item in items:
                reply += f"\n• {item.name} - ₹{int(item.price)} at {item.restaurant.name}"
        else:
            reply = "No spicy items found. Try 'chilli chicken'!"

    # 7. Best rated restaurants
    elif 'best' in user_msg or 'top' in user_msg or 'rated' in user_msg:
        restos = Restaurant.objects.all().order_by('-rating')[:3]
        if restos:
            reply = "Top rated restaurants: "
            for r in restos:
                reply += f"\n• {r.name} - {r.rating}⭐ {r.cuisine}"
        else:
            reply = "No restaurants found."

    # 8. Specific search - LAST
    elif len(words) <= 3:
        items = Item.objects.filter(Q(name__icontains=user_msg) | Q(description__icontains=user_msg))[:3]
        if items:
            reply = f"Found {user_msg}: "
            for item in items:
                reply += f"\n• {item.name} - ₹{int(item.price)} at {item.restaurant.name}"
        else:
            restos = Restaurant.objects.filter(Q(name__icontains=user_msg) | Q(cuisine__icontains=user_msg))
            if restos:
                reply = f"Restaurants matching '{user_msg}': "
                for r in restos:
                    reply += f"\n• {r.name} - {r.rating}⭐"
            else:
                reply = f"No results for '{user_msg}'. Try 'recommend' or 'veg'"

    return JsonResponse({'reply': reply})

import random


from .models import Customer, PasswordResetOTP
from django.contrib import messages

def forgot_password(request):
    storage = messages.get_messages(request)
    storage.used = True  # Clear messages on page load
    if request.method == 'POST':
        mobile = request.POST['mobile']
        try:
            customer = Customer.objects.get(mobile=mobile)
            PasswordResetOTP.objects.filter(user=customer.user).delete() # clear old OTPs
            otp = str(random.randint(100000, 999999))
            PasswordResetOTP.objects.create(user=customer.user, otp=otp)
            print(f"OTP for {mobile}: {otp}")  # Terminal only
            request.session['reset_mobile'] = mobile
            return redirect('verify_otp')
        except Customer.DoesNotExist:
            messages.error(request, "Mobile number not registered")
    return render(request, 'delivery/forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST['otp']
        mobile = request.session.get('reset_mobile')
        if not mobile:
            return redirect('forgot_password')
        try:
            customer = Customer.objects.get(mobile=mobile)
            otp_obj = PasswordResetOTP.objects.filter(user=customer.user).last()
            if otp_obj and otp_obj.otp == otp_entered and otp_obj.is_valid():
                request.session['otp_verified'] = True
                return redirect('reset_password')
            else:
                messages.error(request, "Invalid or expired OTP")
        except:
            messages.error(request, "Something went wrong")
    return render(request, 'delivery/verify_otp.html')

def resend_otp(request):
    mobile = request.session.get('reset_mobile')
    if not mobile:
        return redirect('forgot_password')
    customer = Customer.objects.get(mobile=mobile)
    PasswordResetOTP.objects.filter(user=customer.user).delete()
    otp = str(random.randint(100000, 999999))
    PasswordResetOTP.objects.create(user=customer.user, otp=otp)
    print(f"Resent OTP for {mobile}: {otp}")
    messages.success(request, "New OTP sent")
    return redirect('verify_otp')



def reset_password(request):
    if not request.session.get('otp_verified'):
        return redirect('forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST['password']
        confirm_password = request.POST.get('confirm_password')  # add this field in html
        mobile = request.session.get('reset_mobile')
        
        # 1. Check if passwords match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'delivery/reset_password.html')
        
        # 2. Validate password using Django validators
        try:
            user = Customer.objects.get(mobile=mobile).user
            validate_password(new_password, user=user)
        except Customer.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('forgot_password')
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return render(request, 'delivery/reset_password.html')
        
        # 3. Set new password
        user.set_password(new_password)
        user.save()
        
        # 4. Clear session
        del request.session['reset_mobile']
        del request.session['otp_verified']
        
        messages.success(request, "Password changed successfully. Login now.")
        return redirect('signin')
    
    return render(request, 'delivery/reset_password.html')
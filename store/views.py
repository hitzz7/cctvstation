from django.shortcuts import render, get_object_or_404, redirect
from .models import Category,Project,ProjectImage,Product,ProductImage,Brand,ProductType,UserProfile,Cart,CartItem,Order,OrderItem
from .forms import ContactForm, SignUpForm, LoginForm, UserProfileForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import secrets
from django.http import JsonResponse
from django.db import transaction

def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    projects = Project.objects.all()
    brands = Brand.objects.filter(is_active=True)
    return render(request,'Warzone/home.html',{'categories': categories,'projects':projects,'products':products,'brands': brands});

def product(request):
    product_types = ProductType.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True).select_related('category', 'product_type')
    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')

    if category_id and category_id != 'all':
        try:
            category = Category.objects.get(id=category_id, is_active=True)
            # Get products from this category and all child categories
            category_ids = [category.id] + [child.id for child in category.get_descendants()]
            products = products.filter(category_id__in=category_ids)
            # Show only this category and its children in the filter
            categories = [category] + list(category.get_descendants())
        except Category.DoesNotExist:
            categories = Category.objects.filter(is_active=True, parent=None)
    else:
        # Show only parent categories
        categories = Category.objects.filter(is_active=True, parent=None)

    if search_query:
        products = products.filter(title__icontains=search_query)

    return render(request, 'Warzone/product.html', {
        'categories': categories,
        'product_types': product_types,
        'products': products,
        'search_query': search_query,
        'selected_category': category_id,
    })

def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            'dvr', 'hdd', 'smps', 'monitor', 'wire', 'images',
            'highlights', 'features', 'specs',
        ).select_related('category', 'product_type'),
        pk=product_id,
        is_active=True,
    )
    images = product.images.all()

    # Add 'products' to context as Product.objects.all() as per instruction
    products = Product.objects.all()

    option_groups = []
    if product.dvr.exists():
        option_groups.append({'key': 'dvr', 'label': 'DVR Options', 'items': product.dvr.all()})
    if product.hdd.exists():
        option_groups.append({'key': 'hdd', 'label': 'HDD Options', 'items': product.hdd.all()})
    if product.smps.exists():
        option_groups.append({'key': 'smps', 'label': 'SMPS Options', 'items': product.smps.all()})
    if product.monitor.exists():
        option_groups.append({'key': 'monitor', 'label': 'Monitor Options', 'items': product.monitor.all()})
    if product.wire.exists():
        option_groups.append({'key': 'wire', 'label': 'Wire Options', 'items': product.wire.all()})

    return render(request, 'Warzone/productdetail.html', {
        'product': product,
        'images': images,
        'option_groups': option_groups,
        'products': products,
    })

def project(request):
    projects = Project.objects.all()
    return render(request, 'Warzone/work.html', {'projects': projects})

def project_detail(request,project_id):
    project = get_object_or_404(Project,pk=project_id)
    images = project.images.all()
    return render(request,'Warzone/gallary.html',{'project':project,'images':images})
    
    


def product_list(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = category.products.all()
    return render(request, 'Warzone/category_detail.html', {'category': category, 'products': products})

def services(request):
    return render(request, 'Warzone/services.html')
def work(request):
    return render(request, 'Warzone/work.html')
def about(request):
    return render(request, 'Warzone/about.html')
def contact(request):
    return render(request, 'Warzone/contact.html')

def gallery(request):
    projects = Project.objects.all()
    return render(request, 'Warzone/gallery.html', {'projects': projects})

def contactc(request):
    camera_products = Product.objects.all()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            project = form.save()  # save to DB, project has estimated_price

            # Get the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            mobile = form.cleaned_data['mobile']
            description = form.cleaned_data['description']

            subject = f'New CCTV Project from {name}'
            message = (
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {mobile}\n"
                f"Message: {description}\n"
            )

            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, ['najus777@gmail.com'])
                return redirect('Warzone:success')
            except Exception as e:
                print(f"Error sending email: {e}")
                return render(request, 'Warzone/contact.html', {'form': form, 'error': 'Error sending email. Try again.'})
    else:
        form = ContactForm()

    return render(request, 'Warzone/contact.html', {'form': form,'camera_products': camera_products})

def success(request):
    return render(request, 'Warzone/success.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # User needs email verification
            user.save()

            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                pickup_location=form.cleaned_data.get('pickup_location', ''),
                city=form.cleaned_data.get('city', '')
            )

            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            request.session['verification_token'] = verification_token
            request.session['verification_user_id'] = user.id

            # Send verification email
            verification_url = f"{request.build_absolute_uri('/verify/')}?token={verification_token}"
            subject = 'Verify your CCTV Station account'
            message = f"""
            Hi {user.first_name},

            Please verify your email address by clicking the link below:

            {verification_url}

            This link will expire in 24 hours.

            Thank you,
            CCTV Station Team
            """

            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
                messages.success(request, 'Account created! Please check your email to verify your account.')
                return redirect('store:login')
            except Exception as e:
                messages.error(request, f'Error sending email: {e}')
                return redirect('store:signup')
    else:
        form = SignUpForm()

    return render(request, 'Warzone/signup.html', {'form': form})


def verify_email(request):
    token = request.GET.get('token')
    stored_token = request.session.get('verification_token')
    user_id = request.session.get('verification_user_id')

    if token and stored_token and token == stored_token and user_id:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()

            # Mark profile as verified
            profile = user.profile
            profile.is_verified = True
            profile.save()

            # Clear session
            del request.session['verification_token']
            del request.session['verification_user_id']

            messages.success(request, 'Email verified successfully! You can now login.')
            return redirect('store:login')
        except User.DoesNotExist:
            messages.error(request, 'Invalid verification link.')
    else:
        messages.error(request, 'Invalid or expired verification link.')

    return redirect('store:login')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('store:dashboard')
                else:
                    messages.error(request, 'Please verify your email before logging in.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'Warzone/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('store:home')


@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'Warzone/dashboard.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('store:dashboard')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'Warzone/edit_profile.html', {'form': form})


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        dvr_id = request.POST.get('dvr')
        hdd_id = request.POST.get('hdd')
        smps_id = request.POST.get('smps')
        monitor_id = request.POST.get('monitor')
        wire_id = request.POST.get('wire')

        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request)

        # Check if item already exists in cart
        cart_item = cart.items.filter(product=product).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
                dvr_id=dvr_id if dvr_id else None,
                hdd_id=hdd_id if hdd_id else None,
                smps_id=smps_id if smps_id else None,
                monitor_id=monitor_id if monitor_id else None,
                wire_id=wire_id if wire_id else None
            )

        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_quantity(),
            'message': 'Item added to cart'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    return render(request, 'Warzone/cart.html', {'cart': cart, 'cart_items': cart_items})


def update_cart_item(request, item_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart_item = get_object_or_404(CartItem, id=item_id)

        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                return JsonResponse({'success': True, 'cart_count': cart_item.cart.get_total_quantity()})

        cart_item.save()
        return JsonResponse({
            'success': True,
            'cart_count': cart_item.cart.get_total_quantity(),
            'item_total': cart_item.get_total(),
            'cart_total': cart_item.cart.get_total()
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})


def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart = cart_item.cart
        cart_item.delete()
        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_quantity(),
            'cart_total': cart.get_total()
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, 'Your cart is empty')
        return redirect('store:cart')

    # Get user profile for pre-filling
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', profile.phone)
        city = request.POST.get('city', profile.city)
        address = request.POST.get('address', profile.pickup_location)
        landmark = request.POST.get('landmark', '')
        notes = request.POST.get('notes', '')

        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.get_total(),
                pickup_location=f"{address}\nLandmark: {landmark}" if landmark else address,
                phone=phone,
                city=city,
                notes=notes
            )

            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    dvr=cart_item.dvr,
                    hdd=cart_item.hdd,
                    smps=cart_item.smps,
                    monitor=cart_item.monitor,
                    wire=cart_item.wire
                )

            # Clear cart
            cart_items.delete()

        messages.success(request, f'Order #{order.order_number} placed successfully!')
        return redirect('store:dashboard')

    return render(request, 'Warzone/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'profile': profile
    })

from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
app_name = 'store'

urlpatterns = [
    path('',views.home, name="home"),
    path('product/', views.product, name='product'),

    path('product_list/<int:category_id>/', views.product_list, name='product_list'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('project_detail/<int:project_id>/', views.project_detail, name='project_detail'),
     path('services/', views.services, name='services'),
       path('about/', views.about, name='about'),
       path('work/', views.project, name='work'),
         path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
        #  path('start /', views.start, name='start'),
         path('contactc/', views.contactc, name='contactc'),
    path('success/', views.success, name='success'),

    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('verify/', views.verify_email, name='verify_email'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    # Cart URLs
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),

    # Checkout URL
    path('checkout/', views.checkout, name='checkout'),
]


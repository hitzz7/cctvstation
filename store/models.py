from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User

# Create your models here.
class Category(MPTTModel):
    """
    Category Table implimented with MPTT.
    """

    name = models.CharField(
        verbose_name=_("Category Name"),
        help_text=_("Required and unique"),
        max_length=255,
        unique=True,
    )
    
    
    slug = models.SlugField(verbose_name=_("Category safe URL"), max_length=255, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)
    

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def get_absolute_url(self):
        if self.parent:
            return reverse('store:subcategory_products', args=[self.parent.slug, self.slug])
        return reverse('store:category_products', args=[self.slug])

    def __str__(self):
        return self.name

class ProductType(models.Model):
    """
    ProductType Table will provide a list of the different types
    of products that are for sale.
    """

    name = models.CharField(verbose_name=_("Product Name"), help_text=_("Required"), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")

    def __str__(self):
        return self.name

class DVRType(models.Model):
    """
    DVRType model for specifying types of DVRs, e.g., 4 Channel, 8 Channel, etc.
    """
    name = models.CharField(max_length=50, unique=True)
    channels = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Number of camera channels, e.g. 4 for 4 Channel DVR',
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='dvr_types/', blank=True, null=True)

    def __str__(self):
        return self.name
   

class HDDSize(models.Model):
    """
    HDDSize model for specifying hard drive sizes, e.g., 1TB, 2TB, 4TB, etc.
    """
    name = models.CharField(max_length=20, unique=True)  # e.g., '1TB', '2TB', etc.
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Added price field
    image = models.ImageField(upload_to='hdd_sizes/', blank=True, null=True)  # Added image field

    def __str__(self):
        return self.name

class SMPSOption(models.Model):
    """
    SMPSOption model for specifying types of SMPS (power supplies), e.g., '5A', '10A', etc.
    """
    name = models.CharField(max_length=20, unique=True)  # e.g., '5A', '10A', etc.
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='smps_options/', blank=True, null=True)

    def __str__(self):
        return self.name

class MonitorOption(models.Model):
    """
    MonitorOption model for specifying types of monitors, e.g., '19" LED', '21" LCD', etc.
    """
    name = models.CharField(max_length=50, unique=True)  # e.g., '19" LED', '21" LCD', etc.
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='monitor_options/', blank=True, null=True)

    def __str__(self):
        return self.name

class WireOption(models.Model):
    """
    WireOption model for specifying types of wires, e.g., '90m Copper', '3+1 CCTV Cable', etc.
    """
    name = models.CharField(max_length=50, unique=True)  # e.g., '90m Copper', '3+1 CCTV Cable', etc.
    unit = models.CharField(max_length=20, blank=True)  # e.g., 'meter', 'm', 'foot', 'ft', etc.
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='wire_options/', blank=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.unit})'
   
   


class Product(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.RESTRICT, null=True, blank=True, related_name='products_type')
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    dvr = models.ManyToManyField('DVRType', blank=True, related_name='products_dvr')
    hdd = models.ManyToManyField('HDDSize', blank=True, related_name='products_with_hdd')
    smps = models.ManyToManyField('SMPSOption', blank=True, related_name='products_with_smps')    # Added SMPSOption
    monitor = models.ManyToManyField('MonitorOption', blank=True, related_name='products_with_monitor')  # Added MonitorOption
    wire = models.ManyToManyField('WireOption', blank=True, related_name='products_with_wire')    # Added WireOption

    def __str__(self):
        return self.title
  

    @property
    def discount_percent(self):
        if self.actual_price and self.actual_price > self.price:
            return round((self.actual_price - self.price) / self.actual_price * 100)
        return 0


class ProductHighlight(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='highlights')
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text


class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class ProductSpec(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specs')
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Specification'
        verbose_name_plural = 'Specifications'

    def __str__(self):
        return f'{self.label}: {self.value}'

    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_feature = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.title}"

  
class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/')
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    
class Project(models.Model):
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/')
    is_feature = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.project.title}"

    
    
class StartaProject(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=150)
    description = models.TextField(blank=False)

    # CCTV options


    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    pickup_location = models.TextField(blank=True, help_text='Full pickup address')
    city = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Cart"
        return f"Session Cart ({self.session_key})"

    def get_total(self):
        return sum(item.get_total() for item in self.items.all())

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    dvr = models.ForeignKey(DVRType, on_delete=models.SET_NULL, null=True, blank=True)
    hdd = models.ForeignKey(HDDSize, on_delete=models.SET_NULL, null=True, blank=True)
    smps = models.ForeignKey(SMPSOption, on_delete=models.SET_NULL, null=True, blank=True)
    monitor = models.ForeignKey(MonitorOption, on_delete=models.SET_NULL, null=True, blank=True)
    wire = models.ForeignKey(WireOption, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    def get_total(self):
        total = self.product.price * self.quantity
        if self.dvr:
            total += self.dvr.price * self.quantity
        if self.hdd:
            total += self.hdd.price * self.quantity
        if self.smps:
            total += self.smps.price * self.quantity
        if self.monitor:
            total += self.monitor.price * self.quantity
        if self.wire:
            total += self.wire.price * 25 * self.quantity  # 25m per camera
        return total


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pickup_location = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        import uuid
        return str(uuid.uuid4())[:8].upper()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    dvr = models.ForeignKey(DVRType, on_delete=models.SET_NULL, null=True, blank=True)
    hdd = models.ForeignKey(HDDSize, on_delete=models.SET_NULL, null=True, blank=True)
    smps = models.ForeignKey(SMPSOption, on_delete=models.SET_NULL, null=True, blank=True)
    monitor = models.ForeignKey(MonitorOption, on_delete=models.SET_NULL, null=True, blank=True)
    wire = models.ForeignKey(WireOption, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    def get_total(self):
        total = self.price * self.quantity
        if self.dvr:
            total += self.dvr.price * self.quantity
        if self.hdd:
            total += self.hdd.price * self.quantity
        if self.smps:
            total += self.smps.price * self.quantity
        if self.monitor:
            total += self.monitor.price * self.quantity
        if self.wire:
            total += self.wire.price * 25 * self.quantity
        return total
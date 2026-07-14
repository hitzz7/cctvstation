from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import (
    Brand,
    Category,
    DVRType,
    HDDSize,
    MonitorOption,
    Order,
    OrderItem,
    Product,
    ProductFeature,
    ProductHighlight,
    ProductImage,
    ProductSpec,
    ProductType,
    Project,
    ProjectImage,
    SMPSOption,
    StartaProject,
    UserProfile,
    WireOption,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductHighlightInline(admin.TabularInline):
    model = ProductHighlight
    extra = 2
    fields = ('text', 'order')


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 2
    fields = ('title', 'description', 'order')


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 3
    fields = ('label', 'value', 'order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
        ProductHighlightInline,
        ProductFeatureInline,
        ProductSpecInline,
    ]
    list_display = ('title', 'category', 'product_type', 'actual_price', 'price', 'stock', 'is_active')
    list_filter = ('is_active', 'category', 'product_type')
    search_fields = ('title', 'description')
    list_editable = ('stock', 'is_active')
    autocomplete_fields = ('category', 'product_type')
    filter_horizontal = ('dvr', 'hdd', 'smps', 'monitor', 'wire')
    fieldsets = (
        (None, {
            'fields': ('title', 'category', 'product_type', 'description', 'is_active', 'stock'),
        }),
        ('Pricing', {
            'fields': ('actual_price', 'price'),
        }),
        ('Package Options', {
            'fields': ('dvr', 'hdd', 'smps', 'monitor', 'wire'),
        }),
    )


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    mptt_level_indent = 20
    fields = ('name', 'slug', 'image', 'parent', 'is_active')


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)


@admin.register(DVRType)
class DVRTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'channels', 'price', 'has_image')
    search_fields = ('name',)
    fields = ('name', 'channels', 'price', 'image')

    @admin.display(boolean=True, description='Image')
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(HDDSize)
class HDDSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'has_image')
    search_fields = ('name',)
    fields = ('name', 'price', 'image')

    @admin.display(boolean=True, description='Image')
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(SMPSOption)
class SMPSOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'has_image')
    search_fields = ('name',)
    fields = ('name', 'price', 'image')

    @admin.display(boolean=True, description='Image')
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(MonitorOption)
class MonitorOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'has_image')
    search_fields = ('name',)
    fields = ('name', 'price', 'image')

    @admin.display(boolean=True, description='Image')
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(WireOption)
class WireOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'has_image')
    search_fields = ('name',)
    fields = ('name', 'price', 'image')

    @admin.display(boolean=True, description='Image')
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('name',)


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectImageInline]
    list_display = ('title', 'date_created')
    search_fields = ('title', 'description')


@admin.register(StartaProject)
class StartaProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile')
    search_fields = ('name', 'email', 'mobile', 'description')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'city', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    readonly_fields = ('created_at', 'updated_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'dvr', 'hdd', 'smps', 'monitor', 'wire')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'city', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email', 'phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total_amount', 'created_at', 'updated_at')
        }),
        ('Contact Details', {
            'fields': ('phone', 'city', 'pickup_location')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_total')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__title')
    readonly_fields = ('created_at',)

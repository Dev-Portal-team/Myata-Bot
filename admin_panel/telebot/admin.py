from django.contrib import admin
from django.contrib.admin import AdminSite, ModelAdmin
from django.utils.safestring import mark_safe

from admin_panel.telebot.models import Client, Category, Product, MeasuringDrinks, Order, OrderItem, Booking


class CrmAdminSite(AdminSite):
    site_title = "Управление рестораном"
    site_header = "Управление рестораном"
    index_title = ""


crm_admin = CrmAdminSite()


@admin.register(Client, site=crm_admin)
class ClientAdmin(ModelAdmin):
    list_display = (
        'pk',
        'username',
        'telegram_id',
        'is_blocked',
    )

    list_display_links = ('pk', 'username',)
    empty_value_display = '-пусто-'
    search_fields = ('username', 'pk',)
    list_editable = ('is_blocked',)
    list_filter = ('is_blocked',)

    class Meta:
        verbose_name_plural = 'Гости ресторана'


@admin.register(Category, site=crm_admin)
class CategoryAdmin(ModelAdmin):
    list_display = (
        'title',
    )

    list_display_links = ('title',)
    empty_value_display = '-пусто-'
    search_fields = ('title',)

    class Meta:
        verbose_name_plural = 'Категории'


@admin.register(Product, site=crm_admin)
class ProductAdmin(ModelAdmin):
    list_display = (
        'pk',
        'name',
        'description',
        'category',
        'get_html_image',
        'stock',
    )
    list_display_links = ('pk', 'name')
    list_editable = ('category', 'stock',)
    search_fields = ('name',)
    list_filter = ('created', 'category', 'stock',)
    empty_value_display = '-пусто-'
    fields = (
        'name', 'description', 'photo', 'get_html_image', 'category', 'price', 'stock', 'is_drink',
        'displacement_info',)
    readonly_fields = ('created', 'updated', 'get_html_image', 'displacement_info')

    def get_html_image(self, object):
        if object.photo:
            return mark_safe(f"<img src='{object.photo}' width=50>")

    def displacement_info(self, object):
        if object.is_drink:
            texts = []
            for displacement in object.displacement.all():
                texts.append(f'<p>{displacement.displacement}мл - {displacement.price} р.</p>')
            return mark_safe("".join(texts))

    displacement_info.short_description = "Расценка литража"
    get_html_image.short_description = "Фото"

    class Meta:
        verbose_name_plural = 'Товары ресторана'


@admin.register(MeasuringDrinks, site=crm_admin)
class MeasuringDrinksAdmin(ModelAdmin):
    list_display = (
        'name',
        'displacement',
        'price',
        'product',
    )
    list_display_links = ('name',)
    empty_value_display = '-пусто-'
    search_fields = ('name', 'displacement',)
    list_filter = ('name', 'displacement',)
    list_editable = ('product',)

    class Meta:
        verbose_name_plural = 'Таблица литража и цены напитка'


@admin.register(Order, site=crm_admin)
class OrderAdmin(ModelAdmin):
    list_display = (
        'get_order_number',
        'table',
        'user',
        'status',
        'get_total_cost',
        'get_item_info',
        'comment',
        'get_status_emoji',
    )
    list_display_links = ('table', 'get_order_number',)
    empty_value_display = '-пусто-'
    search_fields = ('user',)
    list_filter = ('table', 'user', 'status',)
    list_editable = ('status',)

    def get_status_emoji(self, object):
        if object.status == "accepted":
            return mark_safe(f"&#128992;")
        elif object.status == "delivered":
            return mark_safe(f"&#9989;")
        elif object.status == "cancelled":
            return mark_safe(f"&#10060;")

    def get_order_number(self, object):
        return mark_safe(f'<p>Заказ {object.pk}</p>')

    def get_item_info(self, object):
        texts = []
        for item in object.items.all():
            if item.product.is_drink:
                texts.append(f'<p>{item.product.name} - {item.displacement}мл {item.quantity}шт. </p>')
            else:
                texts.append(f'<p>{item.product.name} - {item.quantity} шт.</p>')
        return mark_safe("".join(texts))

    get_status_emoji.short_description = ""
    get_item_info.short_description = "Товары в заказе"
    get_order_number.short_description = "Заказ"

    class Meta:
        verbose_name_plural = 'Заказы'


@admin.register(OrderItem, site=crm_admin)
class OrderItemAdmin(ModelAdmin):
    list_display = (
        'pk',
        'order',
        'user',
        'product',
        'get_cost',
        'quantity',
        'get_status_emoji',
    )

    list_display_links = ('order', 'pk',)
    empty_value_display = '-пусто-'
    search_fields = ('user',)
    list_filter = ('user', 'is_order',)
    list_editable = ('product',)

    def get_status_emoji(self, object):
        if object.is_order:
            return mark_safe(f"&#9989;")
        else:
            return mark_safe(f"&#128722;")

    get_status_emoji.short_description = "Статус"

    class Meta:
        verbose_name_plural = 'Выбранные позиции'


@admin.register(Booking, site=crm_admin)
class BookingAdmin(ModelAdmin):
    list_display = (
        'pk',
        'user',
        'quantity_guests',
        'booking_day',
        'phone',
        'get_status_emoji',
    )

    list_display_links = ('user', 'pk',)
    empty_value_display = '-пусто-'
    search_fields = ('phone',)
    list_filter = ('user', 'booking_day',)

    def get_status_emoji(self, object):
        if object.is_confirmed == "accepted":
            return mark_safe(f"&#128992;")
        elif object.is_confirmed == "confirm":
            return mark_safe(f"&#9989;")
        elif object.is_confirmed == "cancelled":
            return mark_safe(f"&#10060;")

    get_status_emoji.short_description = "Статус подтверждения брони"

    class Meta:
        verbose_name_plural = 'Брони ресторана'

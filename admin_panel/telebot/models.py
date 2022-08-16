from aiogram.utils.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения")

    class Meta:
        abstract = True


class Client(CreatedModel):
    username = models.CharField(
        max_length=50,
        help_text='Юзернейм пользователя',
        verbose_name='Юзернейм',
        blank=True,
        null=True,
    )
    telegram_id = models.BigIntegerField(
        help_text='Telegram ID пользователя',
        verbose_name='Telegram ID'
    )
    is_blocked = models.BooleanField(
        help_text='Если стоит галочка то заблокирован',
        verbose_name='Блокировка',
        default=False
    )

    class Meta:
        verbose_name = 'Пользователи телеграмм бота'
        verbose_name_plural = 'Пользователи телеграмм бота'
        ordering = ('-created',)

    def __str__(self):
        return self.username


class Category(models.Model):
    title = models.CharField(
        max_length=200,
        help_text='Название новой категории',
        verbose_name='Название категории'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']


class Product(CreatedModel):
    name = models.CharField(
        max_length=200,
        help_text='Название продукта',
        verbose_name='Название'
    )
    description = models.TextField(
        help_text='Описание продукта',
        verbose_name='Описание'
    )
    photo = models.CharField(
        max_length=200,
        help_text='Ссылка на картинку',
        verbose_name='Картинка',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='products',
        help_text='Категория к которой относится продукт',
        verbose_name='Категория к которой относится продукт'
    )
    price = models.IntegerField(
        help_text='Цена продукта',
        verbose_name='Цена',
        blank=True,
        null=True,
    )
    stock = models.BooleanField(
        help_text='Если стоит галочка то товар не отображается',
        verbose_name='Товар в стоке',
        default=False
    )
    is_drink = models.BooleanField(
        help_text='Если стоит галочка то товар является напитком',
        verbose_name='Является напитком?',
        default=False
    )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.is_drink and self.price:
            raise ValidationError(
                "Для продукта который является напитком цена задается в 'Таблица литража и цены напитка'")

    class Meta:
        verbose_name = 'Продукты ресторана'
        verbose_name_plural = 'Продукты ресторана'
        ordering = ('-created',)

    def __str__(self):
        return self.name


class MeasuringDrinks(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Название напитка',
        verbose_name='Название'
    )
    displacement = models.IntegerField(
        help_text='Вариант литража напитка',
        verbose_name='Литраж',
        default=750,
    )
    price = models.IntegerField(
        help_text='Цена за выбранный литраж',
        verbose_name='Цена',
        default=200,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='displacement',
        help_text='Продукт который относится к литражу',
        verbose_name='Продукт который относится к литражу'
    )

    class Meta:
        verbose_name = 'Таблица литража и цены напитка'
        verbose_name_plural = 'Таблица литража и цены напитка'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Order(CreatedModel):
    THEME_CHOICES = (
        ('accepted', 'Готовится'),
        ('delivered', 'Доставлен гостю'),
        ('cancelled', 'Отменен'),
    )

    table = models.IntegerField(
        help_text='Номер стола к которому относится заказ',
        verbose_name='Столик',
    )
    user = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text='Гость который сделал заказ',
        verbose_name='Гость который сделал заказ'
    )
    status = models.CharField(
        choices=THEME_CHOICES,
        default='accepted',
        max_length=40,
        help_text='Статус заказа',
        verbose_name='Статус',
    )

    class Meta:
        verbose_name = 'Заказы ресторана'
        verbose_name_plural = 'Заказы ресторана'
        ordering = ('-created',)

    def __str__(self):
        return 'Заказ {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name='items',
        blank=True,
        null=True,
        help_text='Заказ к которому относится позиция',
        verbose_name='Заказ к которому относится позиция',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name='order_items',
        blank=True,
        help_text='Цена за 1 еденицу',
        verbose_name='Цена',
    )
    price = models.IntegerField(
        default=1,
        help_text='Цена за 1 еденицу продукта',
        verbose_name='Цена за 1 еденицу продукта',
    )
    quantity = models.IntegerField(
        default=1,
        help_text='Количество продукта',
        verbose_name='Колицество',
    )
    displacement = models.IntegerField(
        help_text='Вариант литража напитка',
        verbose_name='Литраж',
        blank=True,
        null=True,
    )
    is_order = models.BooleanField(
        help_text='Статус заказан или нет',
        verbose_name='Статус заказа',
        default=False
    )

    class Meta:
        verbose_name = 'Позиции выбранные гостем'
        verbose_name_plural = 'Позиции выбранные гостем'

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity


class Booking(CreatedModel):
    user = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='Гость который сделал бронь',
        verbose_name='Гость который сделал бронь'
    )
    quantity_guests = models.IntegerField(
        help_text='Количетсво гостей брони',
        verbose_name='Количетсво гостей',
    )
    start_subscribe = models.DateTimeField(
        verbose_name="Дата брони",
        help_text='Дата брони'
    )
    is_confirmed = models.BooleanField(
        help_text='Статус подтверждена или нет',
        verbose_name='Статус',
        default=False
    )

    class Meta:
        verbose_name = 'Брони ресторана'
        verbose_name_plural = 'Брони ресторана'
        ordering = ('-created',)

    def __str__(self):
        return '{}'.format(self.id)
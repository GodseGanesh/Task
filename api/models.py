from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MenuGroup(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(TimeStampedModel):
    name = models.CharField(max_length=50)
    menu_group = models.ForeignKey(MenuGroup, on_delete=models.CASCADE, related_name="categories")

    class Meta:
        unique_together = ("name", "menu_group")

    def __str__(self):
        return self.name


class Item(TimeStampedModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    # Some items have flexible size/price mapping so we store JSON
    pricing = models.JSONField()  # {"Small":2.5 , "Large":4.0}

    def __str__(self):
        return self.name


class Order(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    order_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    size = models.CharField(max_length=20, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.price * self.quantity


class Payment(TimeStampedModel):
    PAYMENT_METHOD = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("upi", "UPI"),
    ]

    PAYMENT_STATUS = [
        ("completed", "Completed"),
        ("refunded", "Refunded"),
        ("pending", "Pending"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    tips = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["method"]),
        ]

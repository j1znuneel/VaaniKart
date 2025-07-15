from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


CATEGORY_CHOICES = [
    ("fruits", "Fruits"),
    ("vegetables", "Vegetables"),
    ("spices", "Spices"),
    ("grains", "Grains"),
    ("oils", "Oils"),
    ("dairy", "Dairy Products"),
    ("pickles", "Pickles"),
    ("snacks", "Snacks"),
    ("handicrafts", "Handicrafts"),
    ("utensils", "Utensils"),
    ("garments", "Garments"),
    ("home_decor", "Home Decor"),
]
class Product(models.Model):
    """Items available for sale"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    current_stock = models.PositiveIntegerField(default=0)
#    minimum_stock = models.PositiveIntegerField(default=5, help_text="Alert when stock goes below this")
    
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.category}"




"""class Order(models.Model):
    
    ORDER_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled')
    ]

    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=[
        ('COD', 'Cash on Delivery'),
        ('UPI', 'UPI Payment'),
        ('CARD', 'Credit/Debit Card')
    ])
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"""

"""class OrderItem(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
   
        if not self.pk:  # Only on creation
            self.product.current_stock -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
"""
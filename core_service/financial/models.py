import uuid
from django.db import models
from django.core.exceptions import ValidationError

class PaymentMode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Currency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.code} - {self.name}"

class SubscriptionPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    store = models.ForeignKey('inventory.Store', on_delete=models.CASCADE)
    customer_id = models.UUIDField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.SET_NULL, null=True)
    is_credit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Sale {self.id} - {self.company.name}"

class SaleItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"SaleItem {self.id} - {self.product.name}"

class Purchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    store = models.ForeignKey('inventory.Store', on_delete=models.CASCADE)
    supplier_id = models.UUIDField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.SET_NULL, null=True)
    is_credit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Purchase {self.id} - {self.company.name}"

class PurchaseItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"PurchaseItem {self.id} - {self.product.name}"

class ExpenseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    is_credit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Expense {self.id} - {self.company.name}"

class Payable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True, blank=True)
    expense = models.ForeignKey(Expense, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payable {self.id} - {self.company.name}"
    def clean(self):
        if self.purchase and self.expense:
            raise ValidationError("A payable can be associated with either a purchase or an expense, not both.")
        if not (self.purchase or self.expense):
            raise ValidationError("A payable must be associated with either a purchase or an expense.")

class Receivable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Receivable {self.id} - {self.company.name}"

class Bank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.account_name} - {self.bank_name}"

class PaymentOut(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    payable = models.ForeignKey(Payable, on_delete=models.SET_NULL, null=True, blank=True)
    expense = models.ForeignKey(Expense, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.SET_NULL, null=True)
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"PaymentOut {self.id} - {self.company.name}"
    def clean(self):
        if self.payable and self.expense:
            raise ValidationError("A payment out can be associated with either a payable or an expense, not both.")
        if not (self.payable or self.expense):
            raise ValidationError("A payment out must be associated with either a payable or an expense.")

class PaymentIn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    receivable = models.ForeignKey(Receivable, on_delete=models.SET_NULL, null=True, blank=True)
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.SET_NULL, null=True)
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"PaymentIn {self.id} - {self.company.name}"
    def clean(self):
        if self.receivable and self.sale:
            raise ValidationError("A payment in can be associated with either a receivable or a sale, not both.")
        if not (self.receivable or self.sale):
            raise ValidationError("A payment in must be associated with either a receivable or a sale.")

class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100)
    data = models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Report {self.id} - {self.report_type} for {self.company.name}"
from django.db import models
from django_countries.fields import CountryField
from moneyed import Money

from .utils import square_date, square_datetime


class Unit(models.Model):
    token = models.CharField(max_length=13, primary_key=True, editable=False)
    location_name = models.CharField(max_length=512, blank=True)
    receipt_color_code = models.CharField(max_length=7, blank=True)
    address = models.JSONField(blank=True)
    country = CountryField(blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def json_data_map(cls, data):
        return (
            {"token": data["token"]},
            {
                "location_name": data.get("locationName") or "",
                "receipt_color_code": data.get("receiptColorCode") or "",
                "country": data.get("country") or "",
                "address": data.get("address") or {},
                "email": data.get("email") or "",
                "phone_number": data.get("phoneNumber") or "",
            },
        )

    def __str__(self):
        return self.location_name


class Invoice(models.Model):
    token = models.CharField(max_length=22, primary_key=True, editable=False)
    unit = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices"
    )
    name = models.CharField(max_length=512)
    number = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    due_on = models.DateField()
    # receipt_pdf = FileAttachmentField(upload_to="square/receipts/")
    cart = models.JSONField()
    customer = models.JSONField()
    data = models.JSONField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def json_data_map(cls, data):
        return (
            {"token": data["token"]},
            {
                "name": data["name"],
                "number": data["number"],
                "description": data["description"],
                "paid_at": square_datetime(data.get("paidAt")),
                "sent_at": square_datetime(data["sentAt"]),
                "updated_at": square_datetime(data["updatedAt"]),
                "cancelled_at": square_datetime(data.get("cancelledAt")),
                "due_on": square_date(data["dueOn"]),
                "cart": data["cart"],
                "customer": data["customer"],
                "data": data,
            },
        )

    def __str__(self):
        return self.name

    @property
    def total_amount(self):
        money = self.data.get("cart", {}).get("amounts", {}).get("totalMoney")
        if not money:
            return Money()
        return Money(int(money["amount"]) / 100, money["currencyCode"])


class Attachment(models.Model):
    name = models.CharField(max_length=512)
    extension = models.CharField(max_length=16)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachments",
    )
    size_bytes = models.PositiveIntegerField()
    # file = FileAttachmentField(upload_to="square/attachments/")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def json_data_map(cls, data):
        return (
            {"token": data["token"]},
            {
                "name": data["name"],
                "extension": data["extension"],
                "invoice_id": data["invoiceToken"],
                "size_bytes": data["sizeBytes"],
            },
        )

    @property
    def filename(self):
        return f"{self.name}.{self.extension}"

    def __str__(self):
        return self.filename

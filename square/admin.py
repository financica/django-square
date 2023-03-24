from django.contrib import admin

from . import models


class AttachmentInline(admin.StackedInline):
    model = models.Attachment
    extra = 0
    raw_id_fields = ("file",)


@admin.register(models.Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("__str__", "invoice", "size_bytes", "extension")
    search_fields = ("name",)
    raw_id_fields = ("invoice", "file")


@admin.register(models.Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("__str__", "email", "country", "phone_number")
    search_fields = ("location_name", "email", "phone_number")


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    date_hierarchy = "sent_at"
    list_display = ("__str__", "number", "customer_", "amount_", "sent_at", "paid_")
    inlines = (AttachmentInline,)
    search_fields = ("name", "number")

    def amount_(self, obj):
        return obj.total_amount

    def customer_(self, obj):
        customer_name = f"{obj.customer['name']} <{obj.customer['email']}>"
        if "companyName" in obj.customer:
            customer_name = f"{customer_name} ({obj.customer['companyName']})"

        return customer_name

    def paid_(self, obj):
        return "✓" if obj.paid_at else "✗"

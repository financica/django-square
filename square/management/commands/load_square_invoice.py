import cgi

import requests
from django.core.management.base import BaseCommand
from proto_square_api import get_invoice

from ...models import Attachment, Invoice, Unit


def get_content_disposition_filename(header: str) -> str:
    return cgi.parse_header(header)[1].get("filename", "")


class Command(BaseCommand):
    help = "Load data for one or more Square invoice (by invoice ID)"

    def add_arguments(self, parser):
        parser.add_argument("square_id", nargs="+")

    def handle(self, *args, **options):
        for square_id in options["square_id"]:
            response = get_invoice(square_id)
            assert response["status"]["statusCode"] == "SUCCESS", response

            kw, defaults = Unit.json_data_map(response["unit"])
            unit, created = Unit.objects.get_or_create(**kw, defaults=defaults)
            self.stdout.write(f"{unit} {'created' if created else 'updated'}")

            invoice_data = response["invoice"]
            kw, defaults = Invoice.json_data_map(invoice_data)
            invoice, created = Invoice.objects.get_or_create(
                **kw, defaults={"unit": unit, **defaults}
            )

            pdf_download_token = invoice_data["pdfDownloadToken"]

            # if not invoice.receipt_pdf:
            #     url = f"https://squareup.com/invoices/attachments/download/pdf/{pdf_download_token}"
            #     r = requests.get(url, stream=True)
            #     if r.status_code == 200:
            #         filename = get_content_disposition_filename(
            #             r.headers["content-disposition"]
            #         )
            #         # invoice.set_receipt_pdf(
            #         #     r.raw,
            #         #     filename=filename,
            #         #     source_url=url,
            #         #     metadata={"type": "RECEIPT"},
            #         # )
            #     else:
            #         self.stderr.write(
            #             f"Could not download invoice {invoice.token} as PDF"
            #         )

            for attachment_data in invoice_data.get("attachment", []):
                download_token = attachment_data["downloadToken"]
                kw, defaults = Attachment.json_data_map(attachment_data)
                attachment, created = Attachment.objects.get_or_create(
                    **kw,
                    defaults={"invoice": invoice, **defaults},
                )
                # if not attachment.file:
                #     url = f"https://squareup.com/invoices/attachments/download/{download_token}"
                #     r = requests.get(url, stream=True)
                #     if r.status_code != 200:
                #         self.stderr.write(
                #             f"Could not download attachment {attachment.token}"
                #         )
                #         continue

                #     attachment.set_file(
                #         r.raw,
                #         filename=attachment.filename,
                #         source_url=url,
                #         metadata={"type": "ATTACHMENT_GENERIC"},
                #     )

            self.stdout.write(f"{invoice} {'created' if created else 'updated'}")

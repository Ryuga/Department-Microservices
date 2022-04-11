import os
import asyncio
import qrcode
from starlette.config import Config

from backend.models import Transaction
from backend.utility.api_client import DiscordAPIClient
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from config_file import pricing_row, template_2nd_half, template_1st_half

config = Config(".env")
api = DiscordAPIClient(authorization=f"Bot {config('BOT_TOKEN')}")
conf = ConnectionConfig(
   MAIL_USERNAME="zephyrus-no-reply@christcs.in",
   MAIL_PASSWORD=config("MAIL_PASSWORD"),
   MAIL_PORT=587,
   MAIL_SERVER="smtp.zoho.in",
   MAIL_TLS=True,
   MAIL_SSL=False,
   MAIL_FROM="zephyrus-no-reply@christcs.in"
)


async def get_html_formatted_message(reg_id, programs_selected, qrcode_url, total_value):
    pricing = ""
    for program_name, fee in programs_selected.items():
        pricing = pricing + pricing_row.format(program_name=program_name, fee=fee)
    template = template_2nd_half.format(reg_id=reg_id, pricing=pricing, qrcode_url=qrcode_url, total_value=total_value)
    return template_1st_half + template


async def send_registration_mail(to_address, body):
    message = MessageSchema(
        subject="Zephyrus 3.0 Registration Successful",
        recipients=[to_address],
        html=body,
        subtype="html"
        )
    fm = FastMail(conf)
    await fm.send_message(message)


async def post_transaction_microservice():
    while True:
        transactions = await Transaction.filter(mail_sent=False, status="TXN_SUCCESS").prefetch_related("registration")
        for transaction in transactions:
            registration = transaction.registration
            await registration.fetch_related("student")
            student = registration.student
            await student.fetch_related("user")
            if not registration.qr:
                img = qrcode.make(f"https://dashboard.christcs.in/event/registration/details/{registration.id}/")
                img.save("myqrcode.png")
                resp = api.upload_file(open("myqrcode.png", "rb"))
                if resp:
                    registration.qr = resp["attachments"][0]["url"]
                    await registration.save()
                os.remove("myqrcode.png")
            formatted_email_body = await get_html_formatted_message(
                registration.id,
                transaction.events_selected_json,
                registration.qr,
                transaction.value
            )
            transaction.mail_sent = True
            await transaction.save()
            await send_registration_mail(student.user.email, formatted_email_body)
        await asyncio.sleep(20)

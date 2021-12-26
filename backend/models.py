from tortoise import fields
from tortoise.models import Model


class User(Model):
    first_name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=50)

    class Meta:
        table = "auth_user"


class Student(Model):
    user = fields.OneToOneField("models.User", on_delete=fields.CASCADE)

    class Meta:
        table = "dashboard_student"


class Registration(Model):
    id = fields.CharField(pk=True, max_length=9)
    student = fields.ForeignKeyField("models.Student")
    qr = fields.CharField(null=True, max_length=200)

    class Meta:
        table = "dashboard_registration"


class Program(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50)
    reg_fee = fields.IntField()

    class Meta:
        table = "dashboard_program"


class Transaction(Model):
    id = fields.CharField(max_length=9, pk=True)
    status = fields.CharField(max_length=15)
    mail_sent = fields.BooleanField(default=False)
    registration = fields.ForeignKeyField("models.Registration", on_delete=fields.CASCADE)
    events_selected = fields.ManyToManyField("models.Program")
    events_selected_json = fields.JSONField(null=True)
    value = fields.FloatField()

    class Meta:
        table = "dashboard_transaction"

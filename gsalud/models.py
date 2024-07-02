from email.policy import default
from django.db import models
from bulk_update_or_create import BulkUpdateOrCreateQuerySet


class Config(models.Model):
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    mod_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'configs'


class Role(models.Model):
    title = models.CharField()
    description = models.CharField()
    configs = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'roles'


class User(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    id_role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, db_column='id_role', null=True, default=None)
    available = models.BooleanField(default=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    user_pass = models.TextField()
    email_corp = models.CharField(max_length=100, blank=True, null=True)
    email_personal = models.CharField(max_length=100, blank=True, null=True)
    cuil = models.CharField(max_length=12, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    phone_alt = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(auto_now_add=True,)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'users'

    def __str__(self) -> str:
        return self.user_name


class Notification(models.Model):
    title = models.CharField(max_length=10)
    not_text = models.TextField()

    class Meta:
        db_table = 'notifications'


# Many - Many intermediate table
class UsersNotifications(models.Model):
    id_user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column='id_user')
    id_notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, db_column='id_notification')
    viewed = models.BooleanField(default=False)

    class Meta:
        db_table = 'users_notifications'
        unique_together = ('id_user', 'id_notification')


class Particularity(models.Model):
    part_g_salud = models.TextField(blank=True, null=True)
    part_prevencion = models.TextField(blank=True, null=True)
    mod_prevencion = models.DateField(blank=True, null=True)
    mod_g_salud = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'particularities'


class Provider(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    id_provider = models.BigIntegerField(auto_created=False, primary_key=True)
    id_particularity = models.ForeignKey(
        Particularity, models.DO_NOTHING, db_column='id_particularity', null=True)
    id_coordinator = models.IntegerField(blank=True, null=True)
    cuit = models.CharField(max_length=12, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_location = models.CharField(max_length=50, blank=True, null=True)
    sancor_zone = models.CharField(max_length=100, blank=True, null=True)
    observation = models.TextField(blank=True, null=True)
    priority = models.CharField(
        max_length=20, default=None, blank=True, null=True)

    class Meta:
        db_table = 'providers'


class Lot(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    id_user = models.ForeignKey(
        User, models.DO_NOTHING, db_column='id_user', blank=True, null=True)
    lot_key = models.CharField(max_length=80)
    status = models.BooleanField()
    date_asignment = models.DateField(blank=True, null=True)
    date_return = models.DateField(blank=True, null=True)
    date_departure = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'lots'


class ReceiptType(models.Model):
    receipt_short = models.CharField(max_length=2)
    receipt_text = models.CharField(max_length=50)

    class Meta:
        db_table = 'receipt_types'


class RecordType(models.Model):
    record_name = models.CharField(max_length=20)
    record_desc = models.CharField(max_length=50)

    class Meta:
        db_table = 'record_types'


class Record(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    id_record = models.BigIntegerField(auto_created=False, primary_key=True)
    id_provider = models.ForeignKey(
        Provider, models.DO_NOTHING, db_column='id_provider')
    id_receipt_type = models.ForeignKey(
        ReceiptType, models.SET_NULL,  db_column='id_receipt_type', blank=True, null=True)
    id_record_type = models.ForeignKey(
        RecordType, models.SET_NULL, db_column='id_record_type', blank=True, null=True)
    date_liquid = models.DateField(blank=True, null=True, default=None)
    date_recep = models.DateField(blank=True, null=True)
    date_audi_vto = models.DateField(blank=True, null=True)
    date_period = models.DateField(blank=True, null=True)
    totcal = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    bruto = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    ivacal = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    prestac_grava = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    debcal = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    inter_debcal = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    debito = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    debtot = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    a_pagar = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    debito_iva = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    receipt_num = models.CharField(max_length=15, blank=True, null=True)
    receipt_date = models.DateField(blank=True, null=True)
    exento = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    gravado = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    iva_factu = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    iva_perce = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    iibb = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    record_total = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    neto_impues = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    resu_liqui = models.FloatField(blank=True, null=True)
    cuenta = models.CharField(max_length=12, blank=True, null=True)
    ambu_total = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    inter_total = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    audit_group = models.IntegerField(blank=True, null=True)
    date_vto_carga = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=15, blank=True, null=True)
    assigned_user = models.CharField(max_length=20, blank=True, null=True)
    avance = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True)
    hashed_val = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'records'


class RecordInfo(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    id_record = models.ForeignKey(
        Record, models.DO_NOTHING, db_column='id_record')
    id_lot = models.ForeignKey(
        Lot, models.DO_NOTHING, db_column='id_lot', blank=True, null=True)
    date_assignment = models.DateField(blank=True, null=True)
    date_entry_digital = models.DateField(blank=True, null=True)
    date_entry_physical = models.DateField(blank=True, null=True)
    seal_number = models.CharField(
        max_length=100, default=None, blank=True, null=True)
    observation = models.TextField(blank=True, null=True)
    date_close = models.DateField(blank=True, null=True)
    assigned = models.BooleanField(default=False)

    class Meta:
        db_table = 'records_info'


# Many - Many intermediate table
class RecordsInfoUsers(models.Model):
    id_user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column='id_user')
    id_record_info = models.ForeignKey(
        'RecordInfo', on_delete=models.CASCADE, db_column='id_record_info')
    worked_on = models.BooleanField(default=True)

    class Meta:
        db_table = 'users_x_records_info'
        unique_together = ('id_user', 'id_record_info')


class Feedback(models.Model):
    title = models.CharField(max_length=70, null=False)
    date_report = models.DateField(blank=True, null=True, default=None)
    is_bug = models.BooleanField(default=False)
    description = models.TextField(null=False)
    priority = models.IntegerField(default=1)

    class Meta:
        db_table = 'feedback'  # Explicitly define table name (optional)
        ordering = ['priority']  # Order bugs by priority by default

    def __str__(self):
        return self.title

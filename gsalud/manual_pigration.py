from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gsalud', '0004_remove_discrepancies_id_record_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=70)),
                ('date_report', models.DateField(blank=True, default=None, null=True)),
                ('is_bug', models.BooleanField(default=False)),
                ('description', models.TextField()),
                ('priority', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'feedback',
                'ordering': ['priority'],
            },
        ),
        migrations.RenameModel(
            old_name='Lots',
            new_name='Lot',
        ),
        migrations.RenameModel(
            old_name='Users',
            new_name='User',
        ),
        migrations.RenameModel(
            old_name='Providers',
            new_name='Provider',
        ),
        migrations.RenameModel(
            old_name='Configs',
            new_name='Config',
        ),
        migrations.RenameModel(
            old_name='Notifications',
            new_name='Notification',
        ),
        migrations.RenameModel(
            old_name='ReceiptTypes',
            new_name='ReceiptType',
        ),
        migrations.RenameModel(
            old_name='RecordTypes',
            new_name='RecordType',
        ),
        migrations.AlterField(
            model_name='recordinfo',
            name='seal_number',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.RenameModel(
            old_name='Records',
            new_name='Record',
        ),
        migrations.RenameModel(
            old_name='Roles',
            new_name='Role',
        ),
        migrations.DeleteModel(
            name='Priorities',
        ),
    ]

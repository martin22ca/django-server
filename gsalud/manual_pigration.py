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
        migrations.RemoveField(
            model_name='lots',
            name='id_user',
        ),
        migrations.RemoveField(
            model_name='providers',
            name='id_particularity',
        ),
        migrations.RemoveField(
            model_name='providers',
            name='id_priority',
        ),
        migrations.RemoveField(
            model_name='users',
            name='id_role',
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
        migrations.AddField(
            model_name='user',
            name='id_role',
            field=models.ForeignKey(db_column='id_role', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gsalud.role'),
        ),
        migrations.AddField(
            model_name='lot',
            name='id_user',
            field=models.ForeignKey(blank=True, db_column='id_user', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='gsalud.user'),
        ),
        migrations.AlterField(
            model_name='record',
            name='id_provider',
            field=models.ForeignKey(db_column='id_provider', on_delete=django.db.models.deletion.DO_NOTHING, to='gsalud.provider'),
        ),
        migrations.AlterField(
            model_name='recordinfo',
            name='id_lot',
            field=models.ForeignKey(blank=True, db_column='id_lot', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='gsalud.lot'),
        ),
        migrations.AlterField(
            model_name='recordsinfousers',
            name='id_user',
            field=models.ForeignKey(db_column='id_user', on_delete=django.db.models.deletion.CASCADE, to='gsalud.user'),
        ),
        migrations.AlterField(
            model_name='usersnotifications',
            name='id_user',
            field=models.ForeignKey(db_column='id_user', on_delete=django.db.models.deletion.CASCADE, to='gsalud.user'),
        ),
    ]

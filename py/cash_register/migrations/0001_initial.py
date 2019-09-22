# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CashEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_deleted', models.BooleanField(default=False, db_index=True)),
                ('created_date', models.DateTimeField(editable=False, blank=True)),
                ('statement', models.CharField(max_length=8, choices=[(b'income', 'Wp\u0142ata'), (b'expense', 'Wyp\u0142ata')])),
                ('price', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('document_refer', models.CharField(max_length=128, blank=True)),
                ('person_refer', models.CharField(max_length=256, blank=True)),
                ('note', models.TextField(blank=True)),
                ('confirmation', models.BooleanField(default=False)),
                ('confirmation_id', models.CharField(max_length=16, blank=True)),
            ],
            options={
                'ordering': ('created_date',),
                'default_permissions': (),
                'get_latest_by': 'created_date',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_deleted', models.BooleanField(default=False, db_index=True)),
                ('name', models.CharField(max_length=64)),
                ('shortname', models.CharField(max_length=64)),
                ('statement', models.CharField(max_length=8, choices=[(b'income', 'Wp\u0142ata'), (b'expense', 'Wyp\u0142ata')])),
            ],
            options={
                'ordering': ['name'],
                'default_permissions': (),
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='DailyCashSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('balance', models.DecimalField(max_digits=10, decimal_places=2)),
                ('is_locked', models.BooleanField(default=False)),
                ('branch', models.ForeignKey(to='business.Branch')),
            ],
            options={
                'get_latest_by': 'date',
                'permissions': (('view_cashregister', 'Can view cash register'), ('create_cashentry', 'Can create cash entry'), ('update_cashentry', 'Can update cash entry'), ('delete_cashentry', 'Can delete cash entry')),
            },
        ),
        migrations.AddField(
            model_name='cashentry',
            name='category',
            field=models.ForeignKey(to='cash_register.Category'),
        ),
        migrations.AddField(
            model_name='cashentry',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cashentry',
            name='set',
            field=models.ForeignKey(related_name='entries', to='cash_register.DailyCashSet'),
        ),
    ]

# Generated by Django 3.0.4 on 2020-03-29 07:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=255)),
                ('quantity', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('locality', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('pin', models.CharField(max_length=6)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_status', models.IntegerField(default=0)),
                ('acceptance_type', models.CharField(max_length=25)),
                ('order_item_status', models.BooleanField(default=0)),
                ('user_finalised', models.BooleanField(default=0)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('item_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apisv1.Items')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apisv1.Shop')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VolunteerShops',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apisv1.Shop')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VolunteerOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apisv1.UserOrder')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ItemComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.TextField()),
                ('comment_for', models.CharField(max_length=12)),
                ('status', models.BooleanField(default=0)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apisv1.Items')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=0)),
                ('feedback', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apisv1.UserOrder')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
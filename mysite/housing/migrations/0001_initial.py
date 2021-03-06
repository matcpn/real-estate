# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-14 18:21
from __future__ import unicode_literals

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
            name='FlatPriceUpgrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name of the upgrade', max_length=100)),
                ('price', models.FloatField(help_text='price of upgrade')),
                ('image', models.ImageField(default='media/no-img.png', upload_to=b'')),
            ],
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name of the house', max_length=100)),
                ('sqft', models.IntegerField()),
                ('price', models.FloatField()),
                ('image', models.ImageField(default='media/no-img.png', upload_to=b'')),
            ],
        ),
        migrations.CreateModel(
            name='Lot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name of the lot', max_length=100)),
                ('image', models.ImageField(default='media/no-img.png', upload_to=b'')),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PricePerSquareFootUpgrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name of the material', max_length=100)),
                ('ppsf', models.FloatField(help_text='price per square foot')),
                ('image', models.ImageField(default='media/no-img.png', upload_to=b'')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='media/no-img.png', upload_to=b'')),
                ('sqft', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UserChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('house', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='housing.House')),
                ('lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='housing.Lot')),
            ],
        ),
        migrations.CreateModel(
            name='UserRoomUpgradeMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flat_price_upgrade', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='housing.FlatPriceUpgrade')),
                ('ppsf_upgrade', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='housing.PricePerSquareFootUpgrade')),
            ],
        ),
        migrations.CreateModel(
            name='Bathroom',
            fields=[
                ('room_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='housing.Room')),
                ('name', models.CharField(help_text='name of the kitchen', max_length=100)),
            ],
            bases=('housing.room',),
        ),
        migrations.CreateModel(
            name='Bedroom',
            fields=[
                ('room_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='housing.Room')),
                ('name', models.CharField(help_text='name of the bedroom', max_length=100)),
            ],
            bases=('housing.room',),
        ),
        migrations.CreateModel(
            name='DiningRoom',
            fields=[
                ('room_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='housing.Room')),
                ('name', models.CharField(help_text='name of the dining room', max_length=100)),
            ],
            bases=('housing.room',),
        ),
        migrations.CreateModel(
            name='Garage',
            fields=[
                ('room_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='housing.Room')),
                ('name', models.CharField(help_text='name of the garage', max_length=100)),
            ],
            bases=('housing.room',),
        ),
        migrations.CreateModel(
            name='Kitchen',
            fields=[
                ('room_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='housing.Room')),
                ('name', models.CharField(help_text='name of the kitchen', max_length=100)),
            ],
            bases=('housing.room',),
        ),
        migrations.CreateModel(
            name='LivingRoom',
            fields=[
                ('room_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='housing.Room')),
                ('name', models.CharField(help_text='name of the living room', max_length=100)),
            ],
            bases=('housing.room',),
        ),
        migrations.AddField(
            model_name='userroomupgrademapping',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='housing.Room'),
        ),
        migrations.AddField(
            model_name='userroomupgrademapping',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='housing.UserChoice'),
        ),
        migrations.AddField(
            model_name='userchoice',
            name='room_upgrades',
            field=models.ManyToManyField(to='housing.UserRoomUpgradeMapping'),
        ),
        migrations.AddField(
            model_name='userchoice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='flat_price_upgrades',
            field=models.ManyToManyField(blank=True, help_text='choose potential upgrades you would like to be made available for this room', to='housing.FlatPriceUpgrade'),
        ),
        migrations.AddField(
            model_name='room',
            name='ppsf_upgrades',
            field=models.ManyToManyField(blank=True, help_text='choose potential upgrades you would like to be made available for this room', to='housing.PricePerSquareFootUpgrade'),
        ),
        migrations.AddField(
            model_name='house',
            name='lot',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='housing.Lot'),
        ),
        migrations.AddField(
            model_name='house',
            name='bathroom',
            field=models.ManyToManyField(blank=True, to='housing.Bathroom'),
        ),
        migrations.AddField(
            model_name='house',
            name='bedroom',
            field=models.ManyToManyField(blank=True, to='housing.Bedroom'),
        ),
        migrations.AddField(
            model_name='house',
            name='diningRoom',
            field=models.ManyToManyField(blank=True, to='housing.DiningRoom'),
        ),
        migrations.AddField(
            model_name='house',
            name='garage',
            field=models.ManyToManyField(blank=True, to='housing.Garage'),
        ),
        migrations.AddField(
            model_name='house',
            name='kitchen',
            field=models.ManyToManyField(blank=True, to='housing.Kitchen'),
        ),
        migrations.AddField(
            model_name='house',
            name='livingRoom',
            field=models.ManyToManyField(blank=True, to='housing.LivingRoom'),
        ),
    ]

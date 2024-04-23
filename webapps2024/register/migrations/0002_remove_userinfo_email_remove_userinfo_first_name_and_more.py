# Generated by Django 5.0.4 on 2024-04-20 20:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='email',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='id',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='username',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='user',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=1000.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='currency',
            field=models.CharField(choices=[('GBP', 'British Pound'), ('USD', 'US Dollar'), ('EUR', 'Euro')], default='GBP', max_length=3),
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_requests', to='register.userinfo')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_requests', to='register.userinfo')),
            ],
        ),
    ]

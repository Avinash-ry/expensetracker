# Generated by Django 4.2.5 on 2024-02-15 07:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
        ('pdx_auth', '0003_pdxuser_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectedApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_app', to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL)),
                ('to_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_app', to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL)),
            ],
        ),
    ]

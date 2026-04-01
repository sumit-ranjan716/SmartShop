from django.db import migrations, models
import uuid


def gen_uuids_email(apps, schema_editor):
    Profile = apps.get_model('users', 'Profile')
    for row in Profile.objects.all():
        row.email_verification_token = uuid.uuid4()
        row.save(update_fields=['email_verification_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='email_verification_token',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(gen_uuids_email, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='profile',
            name='email_verification_token',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='email_verification_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]


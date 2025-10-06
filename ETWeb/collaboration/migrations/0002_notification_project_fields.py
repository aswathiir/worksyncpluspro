# Generated migration for adding project field to Notification model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collaboration', '0001_initial'),
        ('projects', '0010_auto_20251005_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='projects.project'),
        ),
        migrations.AddField(
            model_name='notification',
            name='invitation_token',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification', to='projects.projectinvitationtoken'),
        ),
        migrations.AddField(
            model_name='notification',
            name='data',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]

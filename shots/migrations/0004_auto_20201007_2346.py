# Generated by Django 3.1.1 on 2020-10-07 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shots', '0003_round_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='round',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rounds', to='shots.event'),
        ),
        migrations.AlterField(
            model_name='round',
            name='payee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payees', to='shots.participant'),
        ),
        migrations.AlterField(
            model_name='roundparticipant',
            name='participant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roundParticipant', to='shots.participant'),
        ),
        migrations.AlterField(
            model_name='roundparticipant',
            name='round',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shots.round'),
        ),
    ]

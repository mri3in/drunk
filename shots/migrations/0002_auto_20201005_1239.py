# Generated by Django 3.1.1 on 2020-10-05 05:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shots', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='participant',
            field=models.ManyToManyField(through='shots.RoundParticipant', to='shots.Participant'),
        ),
        migrations.AlterField(
            model_name='round',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rounds', to='shots.event'),
        ),
        migrations.AlterField(
            model_name='round',
            name='payee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payees', to='shots.participant'),
        ),
        migrations.AlterField(
            model_name='roundparticipant',
            name='participant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roundParticipant', to='shots.participant'),
        ),
        migrations.AlterField(
            model_name='roundparticipant',
            name='round',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shots.round'),
        ),
    ]

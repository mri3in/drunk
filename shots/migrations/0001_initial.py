# Generated by Django 3.1.1 on 2020-10-04 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('nickname', models.CharField(max_length=64)),
                ('type', models.BooleanField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('total', models.IntegerField()),
                ('note', models.CharField(max_length=128)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event', to='shots.event')),
                ('payee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payee', to='shots.participant')),
            ],
        ),
        migrations.CreateModel(
            name='RoundParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participant', to='shots.participant')),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='round', to='shots.round')),
            ],
        ),
    ]

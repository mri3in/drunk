from django.db import models

# Create your models here.
class Participant (models.Model):
    name = models.CharField(max_length=64)
    nickname = models.CharField(max_length=64)
    type = models.BooleanField(null=True)

    def __str__ (self):
        return f"{self.name} - {self.nickname}"

class Event (models.Model):
    name = models.CharField(max_length=64)
    date = models.DateField(auto_now=False, auto_now_add=True, editable=False)

    def __str__ (self):
        return f"{self.name} - {self.date}"


class Round (models.Model):
    datetime = models.DateTimeField(auto_now=False, auto_now_add=True, editable=False)
    event = models.ForeignKey(Event, models.SET_NULL, null=True, related_name="rounds")
    total = models.IntegerField(null=True)
    note = models.CharField(max_length=128, null=True)
    payee = models.ForeignKey(Participant, models.SET_NULL, null=True, related_name="payees")
    participant = models.ManyToManyField(Participant, through='RoundParticipant')
    order = models.IntegerField(editable=False)

    def __str__ (self):
        return f"{self.event} - {self.datetime}"

class RoundParticipant (models.Model):
    round = models.ForeignKey(Round, models.SET_NULL, null=True)
    participant = models.ForeignKey(Participant, models.SET_NULL, null=True, related_name="roundParticipant")
    quantity = models.IntegerField()

    def __str__ (self):
        return f"{self.round} - {self.participant}: {self.quantity}"

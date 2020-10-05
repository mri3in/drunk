from django.shortcuts import render
from .models import *

# Create your views here.
def index(request):
    event = Event.objects.order_by('date')[0]
    rounds = event.rounds.all()
    participants = []
    for round in rounds:
        rpList = RoundParticipant.objects.filter(round__id=round.id)
        print(round)
        print(f"rpList: {rpList}")
        for rp in rpList:
            print(rp)
            if rp.participant not in participants:
                participants.append(rp.participant)

    print(participants)
    print(event)
    print(rounds)
    return render(request, 'shots/index.html', {
        "event": event,
        "participants": participants
    })

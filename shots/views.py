from django.shortcuts import render
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.
def index(request):
    lastEvent = Event.objects.order_by('-date')[0]
    events = Event.objects.order_by('-date')
    rounds = lastEvent.rounds.order_by('-datetime')
    lastRound = rounds[0]
    participants = []
    for round in rounds:
        rpList = RoundParticipant.objects.filter(round=round.id)
        print(f"round: {round}")
        print(f"rpList: {rpList}")
        for rp in rpList:
            print(f"roundparticipant : {rp}")
            if rp.participant not in participants:
                participants.append(rp.participant)
    print("---------")
    print(f"participants: {participants}")
    print(f"lastEvent: {lastEvent}")
    print(f"rounds: {rounds}")
    return render(request, 'shots/index.html', {
        "lastEvent": lastEvent,
        "participants": participants,
        "events": events,
        "rounds": rounds,
        "lastRound": lastRound
    })


def addRound(request):
    if request.method == "POST":
        participants = request.POST.getlist('participant')
        quantities = [request.POST['quantity-{}'.format(p)] for p in participants]
        list = zip(participants, quantities)
        # print(f"participants: {participants}")
        # print(f"quantities: {quantities}")
        # return HttpResponseRedirect(reverse("shots:test", args=(participants, quantities,)))
        # return HttpResponseRedirect(reverse("shots:test"))
        return render(request, 'shots/test.html', {
            "participants":participants,
            "quantities":quantities,
            "list": list
        })

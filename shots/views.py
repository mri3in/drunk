from django.shortcuts import render
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import date


# Create your views here.
def index(request):
    lastEvent = Event.objects.order_by('id')[0]
    events = Event.objects.order_by('-date')
    rounds = lastEvent.rounds.order_by('-datetime')
    participants = []
    lastRound = ""
    if rounds:
        lastRound = rounds[0]
        for round in rounds:
            rpList = RoundParticipant.objects.filter(round=round.id)
            # print(f"round: {round}")
            # print(f"rpList: {rpList}")
            for rp in rpList:
                # print(f"roundparticipant : {rp}")
                if rp.participant not in participants:
                    participants.append(rp.participant)
    # print("---------")
    # print(f"participants: {participants}")
    # print(f"lastEvent: {lastEvent}")
    # print(f"rounds: {rounds}")
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
        listZip = list(zip(participants, quantities))
        # print(f"participants: {participants}")
        # print(f"quantities: {quantities}")
        e = Event.objects.get(pk=int(request.POST["event"]))
        payeeForm = Participant.objects.get(pk=int(request.POST["payee"]))
        totalForm = int(request.POST["total"])
        noteForm = str(request.POST["note"])

        if int(request.POST["round"]) == 0:
            ord = e.rounds.count() + 1
            round = Round(total = totalForm, note = noteForm, payee = payeeForm, event = e, order = ord)
            round.save()
        else:
            round = Round.objects.get(pk=int(request.POST["round"]))
            round.total = totalForm
            round.note = noteForm
            round.payee = payeeForm
            round.save()

        rpList = []
        # print(f"list before: {listZip}")
        for p, q in listZip:
            rp = RoundParticipant(round = round, participant = Participant.objects.get(pk=p), quantity = int(q))
            rpList.append(rp)
            rp.save()
        # print(f"list: {listZip}")
        return render(request, 'shots/test.html', {
            "participants":participants,
            "quantities":quantities,
            "list": listZip,
            "rpList": rpList
        })


def addEvent(request):
    if request.method == "POST":
        eventName = request.POST["event-name"].strip()
        if eventName:
            print(eventName)
            newEvent = Event(name = eventName)
            newEvent.save()
        else:
            newEvent = Event(name = str(date.today().strftime("%d/%m/%Y")))
            newEvent.save()
        r = Round(event=newEvent, order=1)
        r.save()
        return HttpResponseRedirect(reverse("shots:index"))



def addParticipant(request):
    if request.method == "POST":
        nameForm = request.POST["participant-name"].strip()
        nicknameForm = request.POST["participant-nickname"].strip()
        typeForm = request.POST.get("participant-type", False)

        p = Participant(name = nameForm, nickname = nicknameForm, type = typeForm)
        p.save()
        roundIdFrom = int(request.POST["round-id"])
        r = Round.objects.get(pk=roundIdFrom)
        rp = RoundParticipant(round=r, participant=p, quantity=0)
        rp.save()
        return HttpResponseRedirect(reverse("shots:index"))

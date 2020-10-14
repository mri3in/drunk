from django.shortcuts import render
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import date
from django.http import HttpResponse, JsonResponse

# Create your views here.
def index(request, **kwarg):
    if kwarg:
        lastEvent = Event.objects.get(pk=int(kwarg['eventId']))
    else:
        lastEvent = Event.objects.order_by('-id')[0]
    events = Event.objects.order_by('-id')
    rounds = lastEvent.rounds.order_by('-order')
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
    if not participants:
        pList = Participant.objects.filter(type = 1)
        for p in pList:
            participants.append(p)
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
        # return render(request, 'shots/test.html', {
        #     "participants":participants,
        #     "quantities":quantities,
        #     "list": listZip,
        #     "rpList": rpList
        # })
        return HttpResponseRedirect(reverse("shots:index"))


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


def calculateBalance(event_id):
    e = Event.objects.get(id=event_id)
    if e:
        rounds = e.rounds.all()
        totalCost = 0
        totalQuantity = 0
        unitPrice = 0
        participantQuantity = {}
        participantCost = {}
        participantExpense = {}
        participantBalance = {}

        for round in rounds:
            if round.total:
                totalCost += round.total
            rpList = RoundParticipant.objects.filter(round = round.id)
            if round.payee:
                payee = round.payee.id
                if str(payee) in participantExpense:
                    participantExpense[str(payee)] = int(participantExpense[str(payee)]) + round.total
                else:
                    participantExpense[str(payee)] = round.total
            for rp in rpList:
                totalQuantity += rp.quantity
                p = rp.participant.id
                if str(p) in participantQuantity:
                    participantQuantity[str(p)] = int(participantQuantity[str(p)]) + rp.quantity
                else:
                    participantQuantity[str(p)] = rp.quantity
        if totalQuantity != 0:
            unitPrice = totalCost / totalQuantity

        for p, q in participantQuantity.items():
            participantCost[str(p)] = int(q) * unitPrice

        for p in participantCost:
            if str(p) in participantExpense:
                b = float(participantExpense[str(p)]) - float(participantCost[str(p)])
            else:
                b = 0 - float(participantCost[str(p)])
            participantBalance[str(p)] = b

        return participantQuantity, participantCost, participantExpense, participantBalance, totalCost


def dashboard(request, eventId):
    events = Event.objects.order_by('-id')
    participantQuantity, participantCost, participantExpense, participantBalance, totalCost = calculateBalance(eventId)
    participants = []
    for key in participantQuantity:
        p = Participant.objects.get(pk=int(key))
        participants.append(p)
    return render(request, 'shots/dashboard.html', {
        "eventId": eventId,
        "events": events,
        "participantQuantity": participantQuantity,
        "participantCost": participantCost,
        "participantExpense": participantExpense,
        "participants": participants,
        "participantBalance": participantBalance,
        "totalCost": totalCost
    })


def dashboard_table(request, eventId):
    participantQuantity, participantCost, participantExpense, participantBalance, totalCost = calculateBalance(eventId)
    participants = []

    for key in participantQuantity:
        p = Participant.objects.get(pk=int(key))
        participants.append(p)
    # print(participants)
    htmlResponse = ''

    for p in participants:
        expense = 0
        cost = 0
        balance = 0
        if str(p.id) in participantExpense:
            expense = participantExpense[str(p.id)]
            # print(f"payee id : {p.id}, expense : {expense}")
        if str(p.id) in participantCost:
            cost = participantCost[str(p.id)]
        if str(p.id) in participantBalance:
            balance = participantBalance[str(p.id)]

        html = '<tr><td name="name">' + p.name + '</td>'
        html += '<td name="expense">' + str(expense) + '</td>'
        html += '<td name="cost">' + str("{:.2f}".format(cost)) + '</td>'
        if int(balance) > 0:
            html += '<td name="balance" class="positive-balance">' + str("{:.2f}".format(balance)) + '</td></tr>'
        elif int(balance) < 0:
            html += '<td name="balance" class="negative-balance">' + str("{:.2f}".format(balance)) + '</td></tr>'
        else:
            html += '<td name="balance">' + str("{:.2f}".format(balance)) + '</td></tr>'
        htmlResponse += html

    response = {
        'response': htmlResponse,
        'totalCost' : totalCost
    }
    return JsonResponse(response)


def getRoundList(request, eventId):
    rounds = Round.objects.filter(event = eventId).order_by('-order')
    lastEvent = Event.objects.order_by('-id')[0]
    html = ''
    if lastEvent.id == eventId:
        html = '<option value=0> + New Round</option>'
    for i, r in enumerate(rounds):
        if i == 0:
            html += '<option value="' + str(r.id) + '" selected> ' + str(r.order) + '</option>'
        else:
            html += '<option value="' + str(r.id) + '"> ' + str(r.order) + '</option>'
    return HttpResponse(html)


def getRoundDetail(request, roundId):
    if int(roundId):
        r = Round.objects.get(pk=int(roundId))
        rpList = RoundParticipant.objects.filter(round = int(roundId))

        pq = {}
        pq['total'] = r.total
        pq['payee'] = r.payee.id
        # pq['payee-name'] = r.payee.name
        pq['note'] = r.note
        pq['pq'] = {}

        for rp in rpList:
            p = str(rp.participant.name) + "-quantity"
            q = rp.quantity
            pq['pq'][str(p)] = q
        return JsonResponse(pq)


def test(request):
    return render (request, 'shots/test.html')

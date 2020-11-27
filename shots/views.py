from django.shortcuts import render
from .models import *
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.urls import reverse
from datetime import date
from django.http import HttpResponse, JsonResponse
import sys, os
from django.conf import settings
from django.core.signing import Signer
from html import unescape
from urllib.request import urlopen
import math

# Create your views here.
def generateSigner():
    signer = Signer(salt='drunk')
    value = None

    with urlopen(os.path.join(settings.STATIC_URL, 'assets/text.txt')) as f:
        hint = f.readline()
        value = signer.sign(hint.rstrip())

    return value


def isAuthenticated (request):
    if 'drinker' in request.session:
        if request.session['drinker'] == generateSigner():
            return True
        else:
            return False
    else:
        return False


def index(request, **kwarg):
    if not isAuthenticated (request):
        return HttpResponseRedirect(reverse("404_drunk"))
    lastEvent = None
    participants = []
    currentParticipant = []
    currentParticipantId = []
    events = None
    rounds = None

    if kwarg:
        lastEvent = Event.objects.get(pk=int(kwarg['eventId']))
    else:
        if Event.objects.order_by('-id'):
            lastEvent = Event.objects.order_by('-id')[0]

    if lastEvent:
        events = Event.objects.order_by('-id')
        rounds = lastEvent.rounds.order_by('-order')

        if rounds:
            for round in rounds:
                rpList = RoundParticipant.objects.filter(round=round.id)
                for rp in rpList:
                    if rp.participant not in participants:
                        participants.append(rp.participant)

    if not participants:
        if Participant.objects.filter(type = 1):
            pList = Participant.objects.filter(type = 1)
            for p in pList:
                participants.append(p)

    if Participant.objects.order_by('name'):
        for p in Participant.objects.exclude(type=1).order_by('-name'):
            currentParticipant.append(str(p.name))
            currentParticipantId.append(str(p.id))

    return render(request, 'shots/index.html', {
        "lastEvent": lastEvent,
        "participants": participants,
        "events": events,
        "rounds": rounds,
        "currentParticipant": currentParticipant,
        "currentParticipantId": currentParticipantId,
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
        newEvent = None
        if not eventName:
            eventName = str(date.today().strftime("%d/%m/%Y"))
        if Event.objects.filter(name = str(eventName)).count() == 0:
            print(eventName)
            newEvent = Event(name = eventName)
            newEvent.save()
            r = Round(event=newEvent, order=1)
            r.save()
            return HttpResponseRedirect(reverse("shots:index"))
        else:
            return JsonResponse({"message": f"Fail to add {eventName}.", "status": "Error"}, status = 400)


def addParticipant(request):
    message = {}
    htmlResponse = ''
    try:
        if request.method == "POST":
            nameForm = str(request.POST["participant-name"].strip()).lower().capitalize()
            nicknameForm = str(request.POST["participant-nickname"].strip())
            typeForm = request.POST.get("participant-type", False)
            event = Event.objects.get(pk=int(request.POST["event-id"]))
            roundIdForm = int(request.POST.get("round-id"))
            currentNameForm = str(request.POST["current-participant-name"].strip()).lower().capitalize()
            currentParticipantId = str(request.POST["current-participant-id"]).split(',')
            ################
            # print(f"nameForm: {nameForm}; nickname : {nicknameForm}; typeForm {typeForm}; event : {event}")
            ###############
            rounds = event.rounds.all()
            events = Event.objects.order_by('-id')
            currentParticipant = []
            # end of var initial

            if int(request.POST["adding-method"]) == 1: # add new participant
                if Participant.objects.filter(name = nameForm).count() == 0:
                    p = Participant(name = nameForm, nickname = nicknameForm, type = typeForm)
                    p.save()

                    for id in currentParticipantId:
                        currentParticipant.append(str(Participant.objects.get(pk=int(id)).name))

                    message['status'] = 'Success'
                    message['message'] = f"{nameForm} is added successfully."
                    message['currentParticipantId'] = request.POST["current-participant-id"]
                    message['currentParticipant'] = currentParticipant

                else:
                    message['status'] = 'Error'
                    message['message'] = f"{nameForm} exists."
                    return JsonResponse(message, status = 400)

            elif int(request.POST["adding-method"]) == 0: # add an existing participant
                if Participant.objects.filter(name = currentNameForm).count() == 1:
                    p = Participant.objects.get(name = currentNameForm)

                    if not p.type:
                        if str(p.id) in currentParticipantId:
                            del currentParticipantId[currentParticipantId.index(str(p.id))]

                        for id in currentParticipantId:
                            currentParticipant.append(str(Participant.objects.get(pk=int(id)).name))

                        message['status'] = 'Success'
                        message['message'] = f"{currentNameForm} is added successfully."
                        message['currentParticipantId'] = currentParticipantId
                        message['currentParticipant'] = currentParticipant
                    else:
                        message['status'] = 'Error'
                        message['message'] = f"{currentNameForm} exists."
                        return JsonResponse(message, status = 400)

                else:
                    message['status'] = 'Error'
                    message['message'] = f"Fail to add {currentNameForm}."
                    return JsonResponse(message, status = 400)

            if p:
                htmlResponse = f"<div class='col-lg-6 col-sm-6 col-6 participant'><div class='form-group'><div class='input-group drunk'><div class='col-lg-5 col-sm-6 col-12' style='display: flex; align-items: center'><span class='d-inline-block text-truncate'>{p.name}</span></div><span class='input-group-btn'><button type='button' class='quantity-left-minus btn btn-number'  data-type='minus' data-field='{p.name}-quantity'><i class='fa fa-minus drunk' aria-hidden='true'></i></button></span><input type='hidden' name='participant' value='{str(p.id)}'><input type='text' id='{p.name}-quantity' name='quantity-{str(p.id)}' class='form-control input-number participant-quantity' value='0' min='0' max='100'><span class='input-group-btn'><button type='button' class='quantity-right-plus btn btn-number' data-type='plus' data-field='{p.name}-quantity'><i class='fa fa-plus drunk' aria-hidden='true'></i></button></span></div></div></div>"

                message['id'] = str(p.id)
                message['name'] = str(p.name)
                message['htmlResponse'] = htmlResponse

            if roundIdForm != 0:
                r = Round.objects.get(pk=roundIdForm)
                rp = RoundParticipant(round=r, participant=p, quantity=0)
                rp.save()

            return JsonResponse(message, status = 200)

    except:
        message['status'] = 'Error'
        message['message'] = f"Unexpected error: {sys.exc_info()}"
        return JsonResponse(message, status = 400)


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
                b = math.ceil(float(participantExpense[str(p)]) - float(participantCost[str(p)]))
            else:
                b = math.floor(0 - float(participantCost[str(p)]))
            participantBalance[str(p)] = b

        return participantQuantity, participantCost, participantExpense, participantBalance, totalCost


def dashboard(request, eventId=0):
    if not isAuthenticated (request):
        return HttpResponseRedirect(reverse("404_drunk"))
    events = None
    participantQuantity = None
    participantCost = None
    participantExpense = None
    participantBalance = None
    totalCost = None
    participants = []

    if eventId != 0:
        participantQuantity, participantCost, participantExpense, participantBalance, totalCost = calculateBalance(eventId)

        if Event.objects.order_by('-id'):
            events = Event.objects.order_by('-id')

        if participantQuantity:
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


def dashboard_table(request, eventId=0):
    participantQuantity = None
    participantCost = None
    participantExpense = None
    participantBalance = None
    totalCost = 0
    participants = []
    htmlResponse = '<tr><td name="name"></td><td name="expense"></td><td name="cost"></td><td name="balance"></td></tr>'

    if eventId != 0:
        participantQuantity, participantCost, participantExpense, participantBalance, totalCost = calculateBalance(eventId)

        totalCost = float(totalCost) * 1000

        for key in participantQuantity:
            p = Participant.objects.get(pk=int(key))
            participants.append(p)

        htmlResponse = ''

        for p in participants:
            expense = 0
            cost = 0
            balance = 0

            if str(p.id) in participantExpense:
                expense = float(participantExpense[str(p.id)]) * 1000
            if str(p.id) in participantCost:
                cost = float(participantCost[str(p.id)]) * 1000
            if str(p.id) in participantBalance:
                balance = float(participantBalance[str(p.id)]) * 1000

            html = '<tr><td name="name">' + p.name + '</td>'
            html += '<td name="expense">' + f'{expense:,.0f}' + '</td>'
            html += '<td name="cost">' + f'{cost:,.0f}' + '</td>'

            if int(balance) > 0:
                html += '<td name="balance" class="positive-balance">' + f'{balance:,.0f}' + '</td></tr>'
            elif int(balance) < 0:
                html += '<td name="balance" class="negative-balance">' + f'{balance:,.0f}' + '</td></tr>'
            else:
                html += '<td name="balance">' + f'{balance:,.0f}' + '</td></tr>'

            htmlResponse += html

    return JsonResponse({
        'response': htmlResponse,
        'totalCost' : f'{totalCost:,.0f}'
    })


def getRoundList(request, eventId):
    rounds = Round.objects.filter(event = eventId).order_by('-order')
    lastEvent = Event.objects.order_by('-id')[0]
    html = ''
    if lastEvent.id == eventId:
        html = '<option value=0 selected> + New Round</option>'
    if rounds:
        for i, r in enumerate(rounds):
            if i == 0 and lastEvent.id != eventId:
                html += '<option value="' + str(r.id) + '" selected> Round ' + str(r.order) + '</option>'
            else:
                html += '<option value="' + str(r.id) + '"> Round ' + str(r.order) + '</option>'
    return HttpResponse(html)


def getRoundDetail(request, roundId):
    if int(roundId):
        r = Round.objects.get(pk=int(roundId))
        rpList = RoundParticipant.objects.filter(round = int(roundId))
        pq = {}
        pq['total'] = r.total
        pq['payee'] = ""
        if r.payee:
            pq['payee'] = r.payee.id
        # pq['payee-name'] = r.payee.name
        pq['note'] = r.note
        pq['pq'] = {}
        pq['pn'] = {}
        htmlResponse = ''

        if not rpList:
            lastEvent = Event.objects.order_by('-id')[0]
            if r.event.id == lastEvent.id:
                pList = Participant.objects.filter(type = 1)
                for p in pList:
                    htmlResponse += f"<div class='col-lg-6 col-sm-6 col-6 participant'><div class='form-group'><div class='input-group drunk'><div class='col-lg-5 col-sm-6 col-12' style='display: flex; align-items: center'><span class='d-inline-block text-truncate'>{p.name}</span></div><span class='input-group-btn'><button type='button' class='quantity-left-minus btn btn-number'  data-type='minus' data-field='{p.name}-quantity'><i class='fa fa-minus drunk' aria-hidden='true'></i></button></span><input type='hidden' name='participant' value='{str(p.id)}'><input type='text' id='{p.name}-quantity' name='quantity-{str(p.id)}' class='form-control input-number participant-quantity' value='0' min='0' max='100'><span class='input-group-btn'><button type='button' class='quantity-right-plus btn btn-number' data-type='plus' data-field='{p.name}-quantity'><i class='fa fa-plus drunk' aria-hidden='true'></i></button></span></div></div></div>"

                    pq['htmlResponse'] = htmlResponse
                    id = str(p.id)
                    name = str(p.name)
                    pq['pq'][str(name)] = 0
                    pq['pn'][str(id)] = name

        else:
            for rp in rpList:
                htmlResponse += f"<div class='col-lg-6 col-sm-6 col-6 participant'><div class='form-group'><div class='input-group drunk'><div class='col-lg-5 col-sm-6 col-12' style='display: flex; align-items: center'><span class='d-inline-block text-truncate'>{rp.participant.name}</span></div><span class='input-group-btn'><button type='button' class='quantity-left-minus btn btn-number'  data-type='minus' data-field='{rp.participant.name}-quantity'><i class='fa fa-minus drunk' aria-hidden='true'></i></button></span><input type='hidden' name='participant' value='{str(rp.participant.id)}'><input type='text' id='{rp.participant.name}-quantity' name='quantity-{str(rp.participant.id)}' class='form-control input-number participant-quantity' value='0' min='0' max='100'><span class='input-group-btn'><button type='button' class='quantity-right-plus btn btn-number' data-type='plus' data-field='{rp.participant.name}-quantity'><i class='fa fa-plus drunk' aria-hidden='true'></i></button></span></div></div></div>"

                pq['htmlResponse'] = htmlResponse
                id = str(rp.participant.id)
                p = str(rp.participant.name)
                q = rp.quantity
                pq['pq'][str(p)] = q
                pq['pn'][str(id)] = p

        return JsonResponse(pq)


def landingPage(request):
    if 'drinker' in request.session:
        if request.session['drinker'] == generateSigner():
            return HttpResponseRedirect(reverse("shots:index"))
    return render (request, 'shots/landingPage.html')


def getHint(request, hint=""):
    escapedHint = unescape(hint)
    if escapedHint:
        result = None

        with urlopen(os.path.join(settings.STATIC_URL, 'assets/text.txt')) as f:
            result = f.readline().decode("utf-8").rstrip()

        if escapedHint == result:
            request.session['drinker'] = generateSigner()
            return HttpResponsePermanentRedirect(reverse("shots:index"))
    return HttpResponse(escapedHint)

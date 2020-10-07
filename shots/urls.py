from django.urls import path
from . import views

app_name = "shots"
urlpatterns = [
    path('', views.index, name="index"),
    path("addRound", views.addRound, name="addRound"),
    path("addEvent", views.addEvent, name="addEvent"),
    path("addParticipant", views.addParticipant, name="addParticipant")
    # path("test", views.test, name="test")
]

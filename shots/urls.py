from django.urls import path
from . import views

app_name = "shots"
urlpatterns = [
    path('', views.index, name="index"),
    path("addRound", views.addRound, name="addRound"),
    path("addEvent", views.addEvent, name="addEvent"),
    path("addParticipant", views.addParticipant, name="addParticipant"),
    path("dashboard/<int:eventId>", views.dashboard, name="dashboard"),
    path("dashboard_table/<int:eventId>", views.dashboard_table, name="dashboard_table")
    # path("test", views.test, name="test")
]

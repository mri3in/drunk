from django.urls import path
from . import views

app_name = "shots"
urlpatterns = [
    # index page
    path('', views.index, name="index"),
    path('<int:eventId>', views.index, name="index_shot"),
    path("addRound", views.addRound, name="addRound"),
    path("addEvent", views.addEvent, name="addEvent"),
    path("addParticipant", views.addParticipant, name="addParticipant"),
    path("getRoundList/<int:eventId>", views.getRoundList, name="get_round_list"),
    path("getRoundDetail/<int:roundId>", views.getRoundDetail, name="get_round_detail"),

    # dashboard page
    path("dashboard/<int:eventId>", views.dashboard, name="dashboard"),
    path("dashboard_table/<int:eventId>", views.dashboard_table, name="dashboard_table"),

    # , path("test", views.test, name="test")
    # 1st page
    path('landingPage', views.landingPage, name="landingPage")
]

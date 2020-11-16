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
    path("dashboard/", views.dashboard, name="dashboard_empty"),
    path("dashboard/<int:eventId>", views.dashboard, name="dashboard"),
    path("dashboard_table/", views.dashboard_table, name="dashboard_table_empty"),
    path("dashboard_table/<int:eventId>", views.dashboard_table, name="dashboard_table"),

    # 1st page
    path('landingPage', views.landingPage, name="landingPage"),
    path('getHint/<str:hint>', views.getHint, name="get_hint"),
    path('getHint/', views.getHint, name="get_hint_empty")
]

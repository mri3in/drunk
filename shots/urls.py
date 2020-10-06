from django.urls import path
from . import views

app_name = "shots"
urlpatterns = [
    path('', views.index, name="index"),
    path("addRound", views.addRound, name="addRound")
    # path("test", views.test, name="test")
]

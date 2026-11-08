from django.urls import path

from .views import event_page


app_name = "eventos"
urlpatterns = [path("", event_page, name="index")]

from django.urls import path
from . import views


urlpatterns = [
    path("", views.index),
    path("users/", views.get_users),
    path("users/import/", views.import_users , name="users_import"),
]

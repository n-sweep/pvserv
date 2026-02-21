from django.urls import include, path

urlpatterns = [
    path("plotviewer/", include("plotviewer.urls")),
]

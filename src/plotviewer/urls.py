from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("plot/", views.plot_create, name="plot_create"),
    path("plot/<int:plot_id>/", views.plot_detail, name="plot_detail"),
    path("plot/<int:plot_id>/item/", views.plot_list_item, name="plot_list_item"),
    path("events/", views.sse_stream, name="sse_stream"),
]

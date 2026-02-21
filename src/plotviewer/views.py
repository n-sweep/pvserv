import json

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .events import broker
from .models import Plot


def index(request):
    plots = Plot.objects.order_by("-created_at")[:20]
    return render(request, "plotviewer/index.html", {"plots": plots})


@csrf_exempt
@require_POST
def plot_create(request):
    plot = Plot.objects.create(json=request.body.decode("utf-8"))
    broker.publish("new-plot", plot.id)
    return HttpResponse(status=201)


def plot_detail(request, plot_id):
    plot = get_object_or_404(Plot, pk=plot_id)
    return render(request, "plotviewer/partials/plot.html", {"plot": plot})


def plot_list_item(request, plot_id):
    plot = get_object_or_404(Plot, pk=plot_id)
    return render(request, "plotviewer/partials/plot_list_item.html", {"plot": plot})


def sse_stream(request):
    def event_generator():
        q = broker.subscribe()
        try:
            while True:
                event_type, data = q.get()
                yield f"event: {event_type}\ndata: {json.dumps({'id': data})}\n\n"
        finally:
            broker.unsubscribe(q)

    response = StreamingHttpResponse(
        event_generator(), content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response

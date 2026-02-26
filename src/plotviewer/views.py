from queue import Empty

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
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
    broker.publish("new-plot", plot)
    return HttpResponse(status=201)


def plot_detail(request, plot_id):
    plot = get_object_or_404(Plot, pk=plot_id)
    return render(request, "plotviewer/partials/plot.html", {"plot": plot})


def sse_stream(_):
    def event_generator():
        q = broker.subscribe()
        yield ": connected\n\n"
        try:
            while True:
                try:
                    event_type, plot = q.get(timeout=1)
                except Empty:
                    continue
                html = render_to_string(
                    "plotviewer/partials/plot_list_item.html", {"plot": plot}
                )
                # SSE data lines cannot contain raw newlines
                data_lines = "\n".join(f"data: {line}" for line in html.splitlines())
                yield f"event: {event_type}\n{data_lines}\n\n"
        finally:
            broker.unsubscribe(q)

    response = StreamingHttpResponse(
        event_generator(), content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response

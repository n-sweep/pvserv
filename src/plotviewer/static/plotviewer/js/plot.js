function renderPlot() {
    const wrapper = document.querySelector('#plot-container [data-plot-json]');
    if (!wrapper) return;

    const jsonStr = wrapper.dataset.plotJson;
    if (!jsonStr) return;

    try {
        const figure = JSON.parse(jsonStr);
        const titleEl = document.getElementById('title-text');
        if (titleEl) titleEl.innerText = (figure.layout && figure.layout.title && figure.layout.title.text) ? '"' + figure.layout.title.text + '"' : '';

        const mainContent = document.getElementById('main-content');
        const style = window.getComputedStyle(mainContent);
        const contWidth = mainContent.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);

        figure.layout = figure.layout || {};
        figure.layout.width = contWidth;
        figure.layout.height = window.innerHeight * 0.9;

        Plotly.purge('plot');
        Plotly.newPlot('plot', figure);
    } catch (e) {
        console.error('Failed to render plot:', e);
    }
}

function renderThumbnails() {
    document.querySelectorAll('.plot-item-preview[data-plot-json]').forEach(function(el) {
        if (el.querySelector('img')) return;
        try {
            const figure = JSON.parse(el.dataset.plotJson);
            figure.layout = figure.layout || {};
            figure.layout.width = 500;
            figure.layout.height = 300;
            Plotly.toImage(figure, {format: 'png', height: 300, width: 500})
                .then(function(dataUrl) {
                    const img = document.createElement('img');
                    img.src = dataUrl;
                    img.style.width = '100%';
                    img.style.pointerEvents = 'none';
                    el.appendChild(img);
                })
                .catch(function(e) {
                    console.error('Failed to render thumbnail:', e);
                });
        } catch (e) {
            console.error('Failed to parse plot JSON:', e);
        }
    });
}

var resizeTimeout;
window.addEventListener('resize', function() {
    const plot = document.getElementById('plot');
    if (!plot || !plot.data) return;
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
        Plotly.Plots.resize('plot');
    }, 100);
});

document.addEventListener('DOMContentLoaded', function() {
    const ci = document.getElementById('connection-indicator');
    const source = new EventSource('/plotviewer/events/');
    source.onopen = function() { if (ci) ci.innerText = '🟢'; };
    var reconnectCheck = null;
    source.onerror = function() {
        if (ci) ci.innerText = '🔴';
        if (!reconnectCheck) {
            reconnectCheck = setInterval(function() {
                if (source.readyState === EventSource.OPEN) {
                    if (ci) ci.innerText = '🟢';
                    clearInterval(reconnectCheck);
                    reconnectCheck = null;
                }
            }, 500);
        }
    };

    renderPlot();
    renderThumbnails();
});

document.body.addEventListener('htmx:afterSettle', function(e) {
    if (e.target.id === 'plot-container') {
        renderPlot();
        renderThumbnails();
    }
});

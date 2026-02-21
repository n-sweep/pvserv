function renderCurrentPlot() {
    const wrapper = document.querySelector('.plot-wrapper');
    if (!wrapper) return;

    const jsonStr = wrapper.dataset.plotJson;
    if (!jsonStr) return;

    try {
        const figure = JSON.parse(jsonStr);
        const container = document.getElementById('plot');
        const rect = container.getBoundingClientRect();

        figure.layout = figure.layout || {};
        figure.layout.width = rect.width || undefined;
        figure.layout.height = rect.height || undefined;
        figure.layout.autosize = true;

        Plotly.newPlot('plot', figure.data, figure.layout, {responsive: true});
    } catch (e) {
        console.error('Failed to render plot:', e);
    }
}

function renderThumbnails() {
    document.querySelectorAll('.plot-item-preview[data-plot-json]').forEach(el => {
        if (el.dataset.rendered) return;
        
        const jsonStr = el.dataset.plotJson;
        if (!jsonStr) return;

        try {
            const figure = JSON.parse(jsonStr);
            Plotly.newPlot(el, figure.data, {
                ...figure.layout,
                width: 200,
                height: 60,
                margin: {l: 0, r: 0, t: 0, b: 0},
                showlegend: false
            }, {staticPlot: true});
            el.dataset.rendered = 'true';
        } catch (e) {
            console.error('Failed to render thumbnail:', e);
        }
    });
}

window.addEventListener('resize', function() {
    const plot = document.getElementById('plot');
    if (plot && plot.data) {
        Plotly.Plots.resize('plot');
    }
});

document.addEventListener('DOMContentLoaded', renderThumbnails);
document.body.addEventListener('htmx:afterSwap', renderThumbnails);

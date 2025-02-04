console.log('loaded');
$(document).ready(function() {

    var currentPlotData = null;
    var socket = io.connect(
        ip_address + ':' + port,
        {transports: ['websocket']}
    );


    function toggleSelected(element) {
        const previouslySelected = document.querySelector('.plot-item.selected');
        if (previouslySelected) { previouslySelected.classList.remove('selected') };
        element.classList.add('selected');
    };


    function elementInteriorSize(element) {
        const style = window.getComputedStyle(element);

        const paddingLeft = parseFloat(style.paddingLeft);
        const paddingRight = parseFloat(style.paddingRight);
        const paddingTop = parseFloat(style.paddingTop);
        const paddingBottom = parseFloat(style.paddingBottom);

        const contHeight = element.clientHeight - paddingTop - paddingBottom;
        const contWidth = element.clientWidth - paddingLeft - paddingRight;

        return [contHeight, contWidth];
    };


    function rgbToHex(rgb) {
        // Extract the RGB components from the string using a regular expression
        const rgbValues = rgb.match(/\d+/g);

        // Convert the components to integers and then to a hex string
        const r = parseInt(rgbValues[0], 10);
        const g = parseInt(rgbValues[1], 10);
        const b = parseInt(rgbValues[2], 10);

        // Return the hex value as a string, formatted as #RRGGBB
        return `#${(1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1).toUpperCase()}`;
    }


    function processPlotyColor(color) {
        if (color.startsWith('rgb(')) {
            return rgbToHex(color)
        } else {
            return color
        };
    };


    function renderPlot(data, relayout=false, height, width) {
        const element = 'plot';
        var parsed = JSON.parse(data.json);

        const date = document.getElementById('created-date');
        const title = document.getElementById('title-text');
        const plotTitle = parsed.layout.title;
        const container = document.getElementById(element);
        const [contHeight, contWidth] = elementInteriorSize(container);

        // set colors
        container.style.backgroundColor = processPlotyColor(parsed.layout.template.layout.paper_bgcolor);
        container.style.setProperty(
            '--li-text-color',
            processPlotyColor(parsed.layout.template.layout.font.color)
        );

        // set the title text
        date.innerText = `${data.created_at}`;
        title.innerText = '';
        if (plotTitle) { title.innerText = `"${plotTitle.text}"` };

        // calculate width & height

        parsed.layout.width = width || parsed.layout.width || contWidth;

        // adjHeight maxes out at 5:3
        var adjHeight = parsed.layout.width * 0.6;
        if (adjHeight > contHeight) { adjHeight = contHeight };

        parsed.layout.height = height || parsed.layout.height || contHeight;  // adjHeight;

        // render or relayout the plot
        if (relayout) {
            Plotly.relayout(element, {
                height: parsed.layout.height,
                width: parsed.layout.width
            });

        } else {
            Plotly.newPlot(element, parsed);
        };

        currentPlotData = data;
    };


    function renderPlotThumbnail(data, callback) {
        // generate a 300x500 png of the given plot
        var parsed = JSON.parse(data.json);
        Plotly.toImage(parsed, { format: 'png', height: 300, width: 500 })
        .then(function(imageData) { callback(imageData) })
        .catch(function(error) {
            console.error('Error generating thumbnail:', error)
        });
    };


    function createPlotListItem(data) {
        const li = document.createElement('li');
        var parsed = JSON.parse(data.json);

        // set colors
        li.style.backgroundColor = processPlotyColor(parsed.layout.template.layout.paper_bgcolor);
        li.style.setProperty(
            '--li-text-color',
            processPlotyColor(parsed.layout.template.layout.font.color)
        );

        li.classList.add('plot-item');
        li.innerText = `${data.created_at}`;

        // create a clickable thumbnail image
        renderPlotThumbnail(data, function(thumbnail) {
            const img = document.createElement('img');
            img.src = thumbnail;
            img.style.width = '200px';
            li.insertBefore(img, li.firstChild);
            li.onclick = () => {
                renderPlot(data);
                toggleSelected(li);
            };
        });

        return li;
    };


    function insertIntoPlotList(plot) {
        // insert a new plot at the top of the list
        const plotsList = document.getElementById('recent-plots');
        li = createPlotListItem(plot);
        plotsList.insertBefore(li, plotsList.firstChild);
        toggleSelected(li);
    };


    function initializePlotList(plots) {
        // initialize the list of plots
        const plotsList = document.getElementById('recent-plots');
        plots.forEach(plot => {
            li = createPlotListItem(plot);
            plotsList.appendChild(li);
        });
        // mark the top plot as selected
        const firstPlotItem = plotsList.querySelector('li');
        if (firstPlotItem) { firstPlotItem.classList.add('selected') };
    };


    socket.on('connect', function() {
        const ci = document.getElementById("connection-indicator");
        ci.innerText = "🟢";
    });

    socket.on('disconnect', function() {
        const ci = document.getElementById("connection-indicator");
        ci.innerText = "🔴";
    });

    socket.on('error', function(error) {
        const ci = document.getElementById("connection-indicator");
        ci.innerText = "⚠️";
        console.error('Error:', error);
    });

    socket.on('initialize', function(data) {

        // if no plots, return and leave page blank
        if (data.length === 0) {
            console.log('no plots to render');
            return;
        };

        // populate the sidebar with list of plots
        initializePlotList(data);
        // render the top plot in the main view
        renderPlot(data[0]);
    });

    socket.on('update', function(data) {
        insertIntoPlotList(data)
        renderPlot(data);
    });

    socket.on('log', function(data) {
        console.log(data);
    });

    // listen for resize
    let resizeTimeout;
    window.addEventListener('resize', function() {
        if (!currentPlotData) {
            console.log('no plot data to resize');
            return;
        };

        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function(){
            renderPlot(currentPlotData, relayout=true)
        }, 100);
    });

});

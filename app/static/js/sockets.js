console.log('loaded');
$(document).ready(function(){
    var socket = io.connect(
        '192.168.0.105:5619',
        {transports: ['websocket']}
    );
    socket.on('connect', function() {
        console.log('connected');
    });
    socket.on('disconnect', function() {
        console.log('disconnected');
    });
    socket.on('error', function(error){
        console.error('Error:', error);
    });
    socket.on('update', function(data){
        console.log('Data:', data);
        var parsed = JSON.parse(data)
        var layout = {
            plot_bgcolor: '#1b1b1b',  // Background color of the plot
            paper_bgcolor: '#1b1b1b',  // Background color of the paper surrounding the plot
            font: {
                color: '#fff'  // Font color
            }
        };
        Plotly.newPlot('graph', parsed, layout);
    });
});

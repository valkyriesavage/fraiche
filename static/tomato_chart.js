var incoming_data = new Array();

$(document).ready(function() {
	// post the new instructions to the watering system
	// TODO

	// graph the new moisture readings
	updater.start();
});

var updater = {
	socket: null,

	start: function() {
		var url = "ws://" + location.host + "/plant/plant_1";
		if ("WebSocket" in window) {
			updater.socket = new WebSocket(url);
		} else {
			updater.socket = new MozWebSocket(url);
		}
		updater.socket.onmessage = function(event) {
			updater.updateIncoming(JSON.parse(event.data));
		}
	},

	updateIncoming: function(incoming) {
		// TODO what is the format of data coming in?
		// TODO update the incoming data variable
		incoming_data = incoming;
                drawChart();
	}
};

google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['time', 'ideal %moisture', 'recorded %moisture'],
          ['Sun',  10,       10],
          ['Mon',  100,      90],
          ['Tue',  80,      90],
          ['Wed',60,      70],
          ['Thu',  20,     60],
          ['Fri',  10,       50],
          ['Sat', 10,      40]
        ]);

	// TODO go over the incoming data variable
	data.setCell(1,1,incoming_data);

        var options = {
          title: 'Tomatoes'
        };

        var chart = new google.visualization.LineChart(document.getElementById('tomato_chart_div'));
        chart.draw(data, options);
      }

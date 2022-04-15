// Dummy code snippet to connect server and fetch data
var net = require('net');

var client = new net.Socket();
client.connect(5000, '127.0.0.1', function() {
	console.log('Connected');
	client.write('GET'); // send acknowledge to request data
});

client.on('data', function(data) {
	console.log('Received: ' + data);
	var jsondata = JSON.parse(data);
	console.log(jsondata.mode);
	client.destroy(); // kill client after server's response
});

client.on('close', function() {
	console.log('Connection closed');
});

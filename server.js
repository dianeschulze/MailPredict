
var port = Number(process.env.PORT || 3000);

var request = require('request');
var engines = require('consolidate');
var express = require('express'),
    app = express();
var bodyParser = require('body-parser');
app.use(bodyParser.json())
var path = require('path');


app.get('/', function(req, res) {
    res.send('Hi I am an email server');
});


app.get('/helloworld', function(req, res) {
    console.log('got hello world request');
    res.end();
});

// on receipt of new email
app.post('/email', function(req, res){
    console.log('got email')
    console.log(req.body)
    console.log(req.body.keys())
    var sender = req.body.FromAddress
    var subject = req.body.Subject
    var body = req.body.BodyPlain
    var time = req.body.ReceivedAt
    console.log(sender, subject, body, time)
    res.end()
});


app.listen(port);


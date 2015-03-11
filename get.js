'use strict';

var casper = require('casper').create();
if (casper.cli.args.length < 1) {
  casper.echo('usage: casperjs get.js BASE');
  casper.exit();
}
var base = parseInt(casper.cli.args[0], 10);
casper.echo('base = ' + base);
var fs = require('fs');

var clickMax = 50;
var progress = 0;

casper.start('http://ask.fm/EzoeRyou', function() {
  this.fill('#more-container', {
    page: Math.max(clickMax*base - 1, 0) | 0
  });
  this.click('#more-container input[name=commit]');
  this.wait(2000);
  ++progress;
  this.echo('progress ' + progress + '/' + clickMax);
});

for (var i = 1; i < clickMax; i++) {
  casper.then(function() {
    this.click('#more-container input[name=commit]');
    this.wait(2000);
    ++progress;
    this.echo('progress ' + progress + '/' + clickMax);
  });
}

var randomFileName = function() {
  var filename = null;
  do {
    filename = 'database/' + (Math.random()*100000 | 0) + '.json';
  } while(fs.exists(filename));
  return filename;
};


casper.then(function() {
  this.page.includeJs('./jquery-2.1.3.min.js');
  var qa = this.evaluate(function() {
    var results = [];
    $('div#common_question_container div.questionBox').each(function() {
      results.push({
        question: $(this).find('div.question').text(),
        answer: $(this).find('div.answer').text(),
        url: $(this).find('div.time a').attr('href')
      });
    });
    return results;
  });
  this.capture('capture.png');
  var name = randomFileName();
  fs.write(name, JSON.stringify(qa));
  this.echo('name = ' + name);
});

casper.run();

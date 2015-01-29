'use strict';

var casper = require('casper').create();
var fs = require('fs');

casper.start('http://ask.fm/EzoeRyou', function() {
});

var clickMax = 200;
var progress = 0;

for (var i = 0; i < clickMax; i++) {
  casper.then(function() {
    this.click('#more-container input[name=commit]');
    this.wait(500);
    ++progress;
    this.echo('progress ' + progress + '/' + clickMax);
  });
}

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
  casper.echo('len(qa) = ' + qa.length);
  fs.write('qa.json', JSON.stringify(qa));
});

casper.run();

'use strict';

var casper = require('casper').create();

if (casper.cli.args.length < 1) {
  casper.echo('usage: casperjs app.js BASE');
  casper.exit();
}
var page = parseInt(casper.cli.args[0], 10);
casper.echo('page = ' + page);

casper.start('http://ask.fm/EzoeRyou', function() {
  this.fill('#more-container', {
    page: page
  });
  this.click('#more-container input[name=commit]');
  this.wait(2000);
});

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
});

casper.run();

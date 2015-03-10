'use strict';

var casper = require('casper').create();
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('ezoe_qa.sqlite3');
var base = parseInt(0, 10);

casper.start('http://ask.fm/EzoeRyou');

var clickMax = 10;
var progress = 0;

for (var i = 0; i < clickMax; i++) {
  casper.then(function() {
    this.fill('#more-container', {
      page: clickMax*base+i
    });
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
  db.serialize(function() {
    for (var item in qa) {
      var exist = false;
      db.each("SELECT * FROM ezoe_qa WHERE url = $url;", { $url: item.url }, function() {
        exist = true;
      });
      if (!exist) {
        db.run("INSERT INTO ezoe_qa (question, answer, url) VALUES ($question, $answer, $url);", {
          $question: item.question,
          $answer: item.answer,
          $url: item.url
        });
      }
    }
  });
});

casper.run();

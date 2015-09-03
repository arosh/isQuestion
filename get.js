'use strict';

var casper = require('casper').create();
var fs = require('fs');

// 読み込み始めるページの番号をコマンドライン引数で与える
if (casper.cli.args.length < 1) {
  casper.echo('usage: casperjs get.js BASE');
  casper.exit();
}
var base = parseInt(casper.cli.args[0], 10);
casper.echo('base = ' + base);

// 一度の実行で50ページまで読む
// メモリが足らないなら小さくするべき
// (ブラウザで「もっと見る」ボタンを50回押した状態を想像してほしい)
var clickMax = 30;
// 進捗
var progress = 0;

casper.start('http://ask.fm/EzoeRyou', function() {
  // 最初のページに載ってるquestionBoxはとりあえず消す
  // → 消すとうまく行かなかった。重複はあとで排除するべき
  // this.evaluate(function() {
  //   $('div#common_question_container div.questionBox').each(function() {
  //     $(this).remove();
  //   });
  // });
  // 読み込み始めるページをフォームに記入する
  this.fill('#more-container', {
    page: Math.max(clickMax*base - 1, 0) | 0
  });
});

for (var i = 0; i < clickMax; i++) {
  // 「もっと見る」ボタンを押す
  casper.then(function() {
    this.click('#more-container input[name=commit]');
    this.wait(2000);
    ++progress;
    this.echo('progress ' + progress + '/' + clickMax);
  });
}

var nextFileName = function() {
  var filename = null;
  for (var i = 0; ; ++i) {
    filename = 'corpus/' + ('0000' + i).slice(-4) + '.json';
    if (!fs.exists(filename)) break
  }
  return filename;
};

casper.then(function() {
  // ローカルにおいているファイルを読み込む
  // どうせask.fmでもjquery使ってるしincludeしなくて良くね？
  // this.page.includeJs('./jquery-2.1.3.min.js');
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
  var name = nextFileName();
  fs.write(name, JSON.stringify(qa));
  this.echo('name = ' + name);
});

casper.run();

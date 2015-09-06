## これはなに？

ask.fmの質問から質問でないものを集める実験

## 結果

`active_learning.py`を見て下さい。

## 使い方

get.js … ask.fmの質問と回答をスクレイピングするスクリプト。一気に全部読み込むとメモリに乗らないのでBASEを変えて分割して取得する

```
casperjs get.js USERNAME BASE
```

ml.py … 回答者が「質問ではない」と返答している質問を「質問ではない質問」として分類する実験。ナイーブベイズでf1=0.43程度。

al.py … 自分でデータセットを作るために能動学習を実装したもの。その時点での分類結果が50%に近いデータ10件に教師データを付与する。ナイーブベイズでf1=0.65程度 (アノテーションの質による)

## License

This software is released under the MIT License.

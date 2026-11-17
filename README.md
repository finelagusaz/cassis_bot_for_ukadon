# カシスbot for うかどん

伺か用ゴースト「カシス」のトークを、Mastodon インスタンス [うかどん](https://ukadon.shillest.net/) へ毎時投稿する bot です。
GitHub Actions 上で SHIORI（YAYA）を呼び出してトークを生成し、Mastodon API で投稿します。

## 仕組み

```
GitHub Actions (毎時17分, windows-latest)
  └ sample.py
      ├ shioricaller.exe で shiori/yaya/yaya.dll に OnMastodonTootRequest を送る
      ├ 応答の Value をトーク本文として取り出す
      └ Mastodon API (POST /api/v1/statuses) で投稿する（公開範囲: 未収載）
```

| パス | 内容 |
| --- | --- |
| `.github/workflows/sample_yaya.yml` | 毎時投稿する workflow |
| `.github/workflows/check.yml` | 辞書チェックと栞の読み込みテスト（push / PR 時） |
| `.github/workflows/reply.yml` | メンションに返事をする workflow |
| `sample.py` | 栞の呼び出しと Mastodon への投稿 |
| `reply.py` | メンションへの返事（Claude API） |
| `shiori/yaya/OnMastodon.dic` | トーク辞書 |
| `tools/check_dic.py` | トーク辞書のチェックスクリプト |
| `shioricaller/` | コマンドラインから SHIORI を呼び出すツール |

## セットアップ

1. うかどんの「設定 → 開発」でアプリを作成し、`write:statuses` 権限のアクセストークンを発行します。
2. リポジトリの Settings → Secrets and variables → Actions に `MASTODON_ACCESS_TOKEN` として登録します。
3. Actions タブの「YAYA Sample」から `Run workflow` で手動投稿し、動作を確認します。

## トークの追加・編集

`shiori/yaya/OnMastodon.dic` の `CassisTalkList` に、1行1トークで追加します。

```
	"新しいトーク。"
```

- さくらスクリプトや `\` は使えません（そのまま文字として投稿されてしまいます）。
- `?` `!` は半角に統一しています。
- 追加後は `python tools/check_dic.py` で重複や書式の誤りがないか確認できます（push 時にも自動で実行されます）。

### トークの選ばれ方

Actions は実行のたびにセーブデータが消えるため、ランダムに選ぶと同じトークが短い間隔で出てしまいます。
そこで workflow の実行番号（`GITHUB_RUN_NUMBER`）からトークを決める方式にしており、全トーク数を N とすると **N 回の投稿（毎時なら約4か月）で全トークが一巡し、その間に同じトークは出ません**。
実行が遅れたり手動実行を挟んだりしても番号は1ずつ進むため、重複しません。
トークを追加・削除すると巡回の順番は変わります（その切り替わり時だけは重複することがあります）。
ローカル実行など実行番号が無いときは、経過時間（時間単位）で代用します。

## メンションへの返事

`reply.py` が5分おきに未処理のメンションを読み、Claude API でカシスの口調の返事を作って返信します（`.github/workflows/reply.yml`）。

- 口調の見本として、トーク辞書から60件を system prompt に入れています。
- 返信の公開範囲と CW は相手の投稿に合わせます。
- 処理したメンションの通知は dismiss します。状態ファイルは持たず、未 dismiss の通知が「未処理」です。

### 必要な Secrets

| 名前 | 内容 |
| --- | --- |
| `MASTODON_ACCESS_TOKEN` | `read:accounts` `read:notifications` `write:notifications` `read:statuses` `write:statuses` |
| `ANTHROPIC_API_KEY` | Claude API のキー |

モデルは既定で `claude-opus-5-5` です。workflow の env に `CLAUDE_MODEL` を足すと変えられます。

### 無限ループ・使いすぎ対策

`reply.py` 冒頭の定数で調整できます。

| 定数 | 既定 | 内容 |
| --- | --- | --- |
| `MAX_REPLIES_PER_USER_PER_HOUR` | 5 | 同じ相手への返信は1時間にこの回数まで |
| `MAX_BOT_POSTS_IN_THREAD` | 6 | 1つのスレッドでカシスが発言する上限 |
| `MAX_REPLIES_PER_RUN` | 10 | 1回の実行で返信する上限 |
| `MAX_MENTION_AGE` | 3時間 | これより古いメンションには返事をしない |

bot アカウントからのメンションには返事をしません。

### 動作確認

Actions タブの「Reply」から `Run workflow` を実行すると、既定では DRY_RUN（返事を作ってログに出すだけで、投稿も dismiss もしない）で動きます。

## ローカルでの確認（Windows）

```powershell
pip install -r requirements.txt
python tools/check_dic.py
python -c "import sample; print(sample.get_message())"   # 投稿せずにトークだけ取得
```

## 運用上の注意

- 公開リポジトリでは、60日間コミットが無いと schedule 実行が自動で無効化されます。投稿 workflow の最後で有効化 API を呼んで防いでいますが、もし止まっていたら Actions タブから再度有効化してください。
- GitHub Actions の schedule は混雑時に数十分遅れたり、まれに実行されなかったりします。

## ライセンス

同梱の各コンポーネントのライセンスは、それぞれのディレクトリの `LICENSE` を参照してください。

- YAYA: `shiori/yaya/LICENSE`, `shiori/yaya/system/LICENSE`
- shioricaller: `shioricaller/LICENSE`

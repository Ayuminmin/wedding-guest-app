# Message for You

平文メッセージとキーワードをローカルに保管し、AES-GCMで暗号化した `public/data.json` だけを静的ホスティングへ配置します。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp keywords.example.json keywords.json
```

`keywords.json` の例を実際のゲスト名と、ゲストに個別に伝える長いキーワードへ置き換えます。メッセージはGit管理されない `data_plain.json` に記入します。

```json
{
  "alice": "Thank you for coming!",
  "bob": "I love you"
}
```

全員共通のメッセージなら `{ "message": "Thank you for coming!" }` と書けます。`data_plain.json` のキーと `keywords.json` のキーを一致させてください。`keywords.json` はJSONの前に `#` から始まるコメント行を置けます。

## 暗号化と確認

```bash
python encrypt.py
python decrypt_local.py
```

暗号化時は `encrypted alice` のように表示され、公開用ファイル `public/data.json` が生成されます。復号テストの結果はローカルの `data_plain_decrypted.json` に書かれます。ページをローカル確認するには、リポジトリのルートでサーバーを起動します。

```bash
python -m http.server 8000
```

`http://localhost:8000/public/` を開いてください。公開時は `public/` の中身（`index.html` と生成済み `data.json`）だけを静的ホスティングの公開ルートへ配置します。GitHub PagesではActionsなどで `public/` をデプロイ成果物にしてください。リポジトリ全体をそのまま公開ルートにしないでください。

## セキュリティ

- `keywords.json` はローカル専用です。絶対に公開・コミットしないでください。
- `data_plain.json` と `data_plain_decrypted.json` もローカル専用です。
- `salt` と `nonce` は暗号化データごとにランダム生成され、公開して問題ありません。秘密はキーワードです。
- 推測されにくい、十分に長くランダムなキーワードをゲストごとに設定してください。短い合言葉はオフライン推測の対象になります。
- ブラウザー内で復号するため、暗号化データやページ自体を改ざんされない配信元を使ってください。
- PBKDF2は互換性のための採用です。本番用途ではArgon2などの鍵導出方式や、サーバー側で扱う場合のHSM／シークレットストアの導入を検討してください。
- 以前に公開した平文データや合言葉は、Git履歴やキャッシュに残る可能性があります。旧合言葉を再利用せず、必要なら履歴からの除去と失効対応を行ってください。

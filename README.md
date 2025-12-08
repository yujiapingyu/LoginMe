# LoginMe - ユーザーログインシステム

FastAPIとReactに基づいたフルスタックユーザー認証システムで、ユーザー登録、ログイン、およびJWTトークン認証機能を実装しています。

体験ページ：[デモサイト](https://japanesetalk.org/login)

## 1. 環境要件

### バックエンド環境

- **Python**: 3.12 またはそれ以上のバージョン
    
- **データベース**: SQLite
    
- **主な依存パッケージ**:
    
    - FastAPI 0.124.0
        
    - SQLAlchemy 2.0.44
        
    - python-jose 3.5.0（JWT処理）
        
    - passlib 1.7.4（パスワード暗号化）
        
    - uvicorn 0.38.0（ASGIサーバー）
        

### フロントエンド環境

- **Node.js**: 25.1.0 またはそれ以上のバージョン
    
- **パッケージマネージャー**: npm
    
- **主な依存パッケージ**:
    
    - React 19.2.0
        
    - React Router DOM 7.10.1
        
    - Axios 1.13.2
        
    - Vite 7.2.4（ビルドツール）
        

## 2. 起動手順

### 1. バックエンドの起動

```shell
# バックエンドディレクトリに移動
cd backend

# 仮想環境を作成
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt

# envファイルをコピー
cp .env.template .env
# コピー後、必要に応じて.env内の環境変数を修正してください

# バックエンドサーバーを起動（開発モード、自動リロード）
uvicorn main:app --reload

# バックエンドサーバーの動作URL: [http://127.0.0.1:8000](http://127.0.0.1:8000)
# APIドキュメントのアドレス: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
```

### 2. フロントエンドの起動

```
# フロントエンドディレクトリに移動
cd frontend

# 依存関係をインストール
npm install

# envファイルをコピー
cp .env.template .env
# コピー後、必要に応じて.env内の環境変数を修正してください

# 開発サーバーを起動
npm run dev

# フロントエンドサービスの動作URL: http://localhost:5173
```

### 3. アプリへのアクセス

ブラウザを開き、`http://localhost:5173` にアクセスしてアプリケーションを使用します。

## 3. 生成AIの使用箇所

本プロジェクトでは、以下の面で生成AIを活用し開発を支援しました：

### 1. **コード構造設計**

- プロジェクト全体のアーキテクチャ計画の支援
    
- バックエンドAPIエンドポイントの設計とRESTful仕様の確認
    
- フロントエンドのルーティング構造とコンポーネント分割の提案
    

### 2. **コード実装**

- **バックエンド**:
    
    - JWTトークンの生成と検証ロジック（`create_access_token`、`get_current_user`関数）
        
    - パスワードの暗号化と検証メカニズム（bcryptを使用）
        
    - データベースモデルとPydanticスキーマの定義
        
- **フロントエンド**:
    
    - React Routerの設定とルート保護ロジック
        
    - APIクライアントのラップ（axios設定）
        
    - フォームバリデーションとエラーハンドリング
        

### 3. **コード最適化**

- Python 3.12+のベストプラクティスに合わせるため、`datetime.utcnow()`から`datetime.now(timezone.utc)`へ移行
    
- 環境変数設定の最適化（dotenvを使用）
    
- コードコメントとドキュメント生成
    

### 4. **デバッグとトラブルシューティング**

- JWTトークンの有効期限処理に関する問題の調査
    
- CORS設定の問題解決
    
- データベース接続とセッション管理の最適化
    

### 5. **ドキュメント**

- ドキュメントの多言語翻訳
    

## 4. 簡易設計説明

### インタラクションフローの確定

```
1. ユーザー登録フロー:
   ユーザーがフォーム入力 → フロントエンド検証 → POST /api/register → バックエンドでメールアドレスの一意性検証 
   → パスワードハッシュ化 → データベースへ保存 → ユーザー情報を返す

2. ユーザーログインフロー:
   ユーザーがフォーム入力 → フロントエンド検証 → POST /api/login → バックエンドでメールアドレスとパスワードを検証
   → 双トークン生成（Access Token + Refresh Token） → access_tokenを返す + refresh_tokenをHttpOnly Cookieに設定
   → フロントエンドでaccess_tokenを内存に保存

3. 保護されたリソースへのアクセス:
   フロントエンドからのリクエスト → JWTトークンを付与（Authorization: Bearer <token>）
   → バックエンドでトークン検証 → ユーザーデータまたは401エラーを返す

4. ページ刷新時の自動トークン更新:
   ページ刷新 → Access Token消失（内存クリア） → API呼び出し時401エラー
   → 拦截器が自動的にRefresh Token（Cookie）でAccess Tokenを更新
   → 新しいAccess Tokenで元のリクエストを再試行 → 成功
```

### バックエンド設計

#### 技術スタック

- **フレームワーク**: FastAPI - モダンで高速なPython Webフレームワーク。非同期処理と自動APIドキュメントをサポート
    
- **ORM**: SQLAlchemy - 強力なPython SQLツールキットおよびオブジェクト関係マッピング
    
- **認証**: JWT (JSON Web Token) - ステートレスなトークン認証メカニズム
    
- **パスワード暗号化**: Bcrypt - 業界標準のパスワードハッシュアルゴリズム
    
- **データ検証**: Pydantic - Pythonの型ヒントに基づいたデータ検証
    

#### データベース設計

```
User テーブル:
- id: Integer (主キー)
- email: String (ユニーク, インデックス)
- hashed_password: String (BCrypt暗号化済み)

RefreshToken テーブル:
- id: Integer (主キー)
- user_id: Integer (外部キー → User.id)
- token: String (ユニーク, インデックス)
- expires_at: DateTime (有効期限)
- created_at: DateTime (作成日時)
```

#### APIインターフェース設計

|エンドポイント|メソッド|機能|認証要否|
|---|---|---|---|
|`/api/register`|POST|ユーザー登録|否|
|`/api/login`|POST|ユーザーログイン|否|
|`/api/refresh`|POST|Access Token更新|要（Refresh Token Cookie）|
|`/api/logout`|POST|ログアウト|否|
|`/api/users/me`|GET|現在のユーザー情報を取得|要（JWT）|

**詳細インターフェース説明:**
1. **POST /api/register**
    
    - リクエストボディ: `{ "email": "user@example.com", "password": "password123" }`
        
    - レスポンス: `{ "id": 1, "email": "user@example.com" }`
        
    - エラー: 400 - メールアドレス登録済み
        
2. **POST /api/login**
    
    - リクエストボディ: `{ "email": "user@example.com", "password": "password123" }`
        
    - レスポンス: `{ "access_token": "eyJ...", "token_type": "bearer" }`
        
    - Cookie設定: `refresh_token` (HttpOnly, 7日間有効)
        
    - エラー: 400 - ユーザーが存在しないか、パスワードが間違っています

3. **POST /api/refresh**
    
    - Cookie: `refresh_token` (自動送信)
        
    - レスポンス: `{ "access_token": "eyJ...", "token_type": "bearer" }`
        
    - エラー: 401 - Refresh Token無効または期限切れ

4. **POST /api/logout**
    
    - Cookie: `refresh_token` (自動送信)
        
    - レスポンス: `{ "message": "Logged out successfully" }`
        
    - 処理: データベースからRefresh Tokenを削除、Cookieをクリア
        
5. **GET /api/users/me**
    
    - リクエストヘッダー: `Authorization: Bearer <token>`
        
    - レスポンス: `{ "id": 1, "email": "user@example.com" }`
        
    - エラー: 401 - 未認証（Unauthorized）
        
2. **POST /api/login**
    
    - リクエストボディ: `{ "email": "user@example.com", "password": "password123" }`
        
    - レスポンス: `{ "access_token": "eyJ...", "token_type": "bearer" }`
        
    - エラー: 400 - ユーザーが存在しないか、パスワードが間違っています
        
3. **GET /api/users/me**
    
    - リクエストヘッダー: `Authorization: Bearer <token>`
        
    - レスポンス: `{ "id": 1, "email": "user@example.com" }`
        
    - エラー: 401 - 未認証（Unauthorized）
        

#### セキュリティメカニズム

- **パスワードの安全性**: Bcryptアルゴリズムを使用してパスワードをハッシュ化し、平文のパスワードは決して保存しません
    
- **双トークンメカニズム**: 
    - **Access Token**: 短期有効（15分）、内存に保存、XSS攻撃から保護
    - **Refresh Token**: 長期有効（7日）、HttpOnly Cookieに保存、JavaScriptからアクセス不可
    
- **トークン検証**: 保護されたリソースへのリクエストごとに、トークンの署名と有効期限を検証します
    
- **自動トークン更新**: Access Token期限切れ時、Refresh Tokenを使用して自動的に新しいAccess Tokenを取得
    
- **トークン撤回**: Refresh Tokenをデータベースに保存し、ログアウト時に削除することで即座に撤回可能
    
- **依存性の注入**: FastAPIの依存性注入システムを使用して認証ガードを実装しています
    
- **CORS設定**: 環境変数で許可するオリジンを設定、クロスオリジンリクエストを制御
    

### フロントエンド設計

#### 技術スタック

- **フレームワーク**: React 19.2.0 - モダンなUIライブラリ
    
- **ルーティング**: React Router DOM 7.10.1 - クライアントサイドのルーティング管理
    
- **HTTPクライアント**: Axios - APIリクエストとレスポンスの処理
    
- **ビルドツール**: Vite - 高速なフロントエンドビルドツール
    

#### ページ構成

```
/login       → ログインページ
/register    → 登録ページ
/            → トップページ（保護対象、ログインが必要）
```

#### コンポーネント設計

- **LoginPage**: ログインフォーム、ユーザーのログインロジックを処理
    
- **RegisterPage**: 登録フォーム、ユーザーの登録ロジックを処理
    
- **HomePage**: 保護されたホームページ、ユーザー情報を表示
    

#### 状態管理とトークン保存

- **Access Token**: 内存に保存、XSS攻撃から最大限に保護
    
- **Refresh Token**: HttpOnly Cookieに保存、JavaScriptからアクセス不可、XSSから完全に保護
    
- **自動トークン更新**: Axiosインターセプターで401エラーを捕捉し、Refresh Tokenで自動的にAccess Tokenを更新
    
- **競合状態の処理**: 複数のリクエストが同時に401を受け取った場合、一度だけRefresh Tokenを実行し、他のリクエストはキューで待機
    
- **ユーザー情報**: React Stateで管理、ページ刷新時は自動的にAPI経由で再取得

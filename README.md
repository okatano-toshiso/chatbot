# 🤖 Chatbot System

宿泊施設向けの **予約・問い合わせ対応チャットボット** です。  
RAG（Retrieval-Augmented Generation）とOpenAI APIを活用し、自然で柔軟な対話を実現します。

---

## 📚 目次

- [概要](#-概要)
- [特徴](#-特徴)
- [システム構成](#-システム構成)
- [ディレクトリ構成](#-ディレクトリ構成)
- [RAD構成（RAG + API + Dialog）](#-rad構成rag--api--dialog)
- [プロンプト設計](#-プロンプト設計)
- [セットアップ手順](#-セットアップ手順)
- [使用方法](#-使用方法)
- [テスト](#-テスト)
- [ライセンス](#-ライセンス)
- [貢献方法](#-貢献方法)

---

## 🧠 概要

このプロジェクトは、宿泊施設の予約・問い合わせ・観光案内・グルメ情報などを自動で対応するチャットボットです。  
RAG構成により、FAQや観光情報などの知識を検索し、OpenAI APIを通じて自然な応答を生成します。

---

## ✨ 特徴

- 🔍 **RAG構成** による高精度な情報検索  
- 💬 **自然言語対話** によるスムーズなユーザー体験  
- 🧩 **モジュール構成** により拡張性が高い  
- 🎯 **宿泊予約・観光案内・FAQ対応** など多目的対応  
- 🧠 **プロンプト設計** による柔軟な会話制御  

---

## 🏗️ システム構成

```
ユーザー入力
   ↓
意図判定 (judge_intent.py)
   ↓
RAG検索 (utils/rag.py)
   ↓
応答生成 (generate.py)
   ↓
出力 (main.py)
```

---

## 📁 ディレクトリ構成

```
chatbot/
├── main.py                        # エントリーポイント
├── chatgpt_api.py                 # OpenAI API連携
├── generate.py                    # 応答生成ロジック
├── menu_items.py                  # メニュー項目定義
├── messages.py                    # メッセージ管理
├── reservation_handler*.py        # 予約関連処理群
├── reservation_status.py          # 予約ステータス管理
├── validation.py                  # 入力検証
├── prompts/                       # プロンプト・RAGデータ
│   ├── judge_*                    # 意図判定
│   ├── data_*                     # FAQ・観光・グルメ情報
│   ├── confirm_*                  # 確認プロンプト
│   ├── execute_reserve.py         # 予約実行
│   ├── text_chunks_*.json         # RAG用テキスト
│   ├── vectors_*.json             # ベクトルデータ
│   └── ...
├── utils/                         # ユーティリティ群
│   ├── rag.py                     # RAG処理
│   ├── transcriber.py             # 音声→テキスト変換
│   ├── clean_phone_number.py      # 電話番号整形
│   ├── vocabulary_filter_utils.py # 禁止語フィルタ
│   └── ...
└── requirements.txt               # 依存パッケージ
```

---

## 🧩 RAD構成（RAG + API + Dialog）

| コンポーネント | 役割 | 対応ファイル |
|----------------|------|---------------|
| **RAG** | 知識検索 | `utils/rag.py` |
| **API** | OpenAI API連携 | `chatgpt_api.py` |
| **Dialog** | 対話制御 | `main.py`, `messages.py` |

この3層構成により、文脈を保持しつつ外部知識を活用した自然な応答を生成します。

---

## 💬 プロンプト設計

`prompts/` フォルダには、各種対話シナリオに対応するプロンプトが定義されています。

| カテゴリ | 例 | 説明 |
|-----------|----|------|
| `judge_*` | `judge_intent.py` | ユーザー意図の分類 |
| `data_*` | `data_faq.py` | FAQ・観光・グルメ情報 |
| `confirm_*` | `confirm_reserve.py` | 予約確認・キャンセル確認 |
| `execute_reserve.py` | - | 実際の予約実行 |
| `inn_faq.py` | - | 宿泊施設に関するFAQ |

---

## ⚙️ セットアップ手順

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

---

## 🚀 使用方法

```bash
# チャットボットの起動
python main.py
```

起動後、コンソールまたはLINE連携などを通じて対話が可能です。

---

## 🧪 テスト

各モジュールは単体で実行可能です。

```bash
python reservation_handler_guest.py
```

---

## 🤝 貢献方法

1. フォークを作成  
2. 新しいブランチを作成 (`feature/your-feature`)  
3. 変更をコミット  
4. プルリクエストを送信  

---

## 📄 ライセンス

このプロジェクトは社内利用を目的としており、外部公開は想定していません。

---

## 👤 作者情報

| 項目 | 内容 |
|------|------|
| **名前** | 岡田 俊宏 (Toshihiro Okada) |
| **GitHub** | [okatano-toshiso](https://github.com/okatano-toshiso) |
| **所属** | SynapseAI |
| **Webサイト** | [https://github.com/okatano-toshiso/synapseai](https://github.com/okatano-toshiso/synapseai) |
| **専門分野** | AIソリューション開発・自然言語処理・自動化システム設計 |

---

### 🧩 作者メッセージ

> 「AIが人の仕事を奪うのではなく、人の創造性を拡張する未来を作りたい。」

このプロジェクトは、SynapseAIのAIソリューション開発の一環として設計されました。  
宿泊業界における自動応答・予約支援・情報検索の最適化を目的とし、  
**RAG × OpenAI × 対話設計** による実用的なAIアシスタントの実現を目指しています。

---

## 🧭 参考資料

> 本READMEは以下の資料を参考に、読みやすさ・構造性・開発者体験を重視して作成されています。

- [GitHub公式: READMEの書き方](https://docs.github.com/ja/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [Qiita: READMEの書き方まとめ](https://qiita.com/shun198/items/c983c713452c041ef787)
- [C++ Learning: READMEの基本構成](https://cpp-learning.com/readme/)
- [Reddit: Good README Templates](https://www.reddit.com/r/programming/comments/l0mgcy/github_readme_templates_creating_a_good_readme_is/?tl=ja)

---

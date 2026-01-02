# 🌷 花言葉図鑑 (Flower Language Encyclopedia)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://flowerapppublic-dc8hdoxcoqzudmntksdnee.streamlit.app/)

366日の誕生花や花言葉を検索できる、Webアプリケーションです。
PythonとStreamlitを使用して開発しました。


## 🚀 主な機能

1.  **💐 本日の誕生花**
    * 日本時間（JST）に基づいて、その日の誕生花を自動表示します。
2.  **📖 植物図鑑・検索**
    * 花の名前一覧から探したり、キーワード（「愛」「希望」など）や日付で検索できます。
3.  **❓ 花言葉クイズ**
    * 「花言葉から花を当てる」「花から花言葉を当てる」2つのモードで遊べます。
4.  **❤️ お気に入り機能**
    * 気になった花を保存して、リスト化できます（セッション内保存）。
5.  **🖼️ 画像自動取得**
    * Wikipedia APIを使用し、植物の画像を動的に取得・表示します。

## 🛠️ 使用技術

* **言語:** Python 3.x
* **フレームワーク:** Streamlit
* **ライブラリ:** Pandas, Requests
* **API:** Wikipedia API (MediaWiki Action API)
* **データ生成:** Google Gemini (生成AI)

## 💡 こだわりポイント（技術・権利関係）

* **著作権への配慮**
    * 掲載されている解説文（由来・豆知識等）は、既存のWebサイトからの転載ではなく、**生成AI（Google Gemini）を使用してゼロから執筆・生成**した独自のデータを使用しています。
    * 画像はWikipedia APIを経由し、ライセンスに従って参照表示しています。
* **Wikipedia API連携**
    * あいまい検索機能を実装し、表記揺れ（例：「バラ」「薔薇」）があっても適切な画像を検索・取得できるロジックを組んでいます。


⚠️ 免責事項
本アプリの情報（花言葉・由来等）は、AIおよび一般的な文献を参考に作成していますが、諸説あるため正確性を完全に保証するものではありません。

本アプリの利用により生じた損害等について、開発者は責任を負いかねます。

© 2026 [tkg-seimei]

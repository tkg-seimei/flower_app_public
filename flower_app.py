import streamlit as st
import pandas as pd
import glob
import random
import requests
import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="花言葉図鑑",
    page_icon="🌷",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ==========================================
# 日本時間（JST）の設定
# ==========================================
JST = datetime.timezone(datetime.timedelta(hours=9))
now_jst = datetime.datetime.now(JST)

# ==========================================
# デザイン調整（config.toml前提）
# ==========================================
# 基本的な配色は .streamlit/config.toml に依存
# ここではグラデーションや枠線などの詳細デザインのみ定義
hide_streamlit_style = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Zen+Old+Mincho:wght@400;700&display=swap');
            
            /* フォント設定 */
            html, body, [class*="css"] {
                font-family: 'Zen Old Mincho', serif; 
            }
            
            /* 背景設定（グラデーション） */
            .stApp { 
                background: linear-gradient(to bottom, #ffffff, #fff0f5); 
            }

            /* 入力ボックス（枠線色指定） */
            .stTextInput > div > div > input, .stSelectbox > div > div > div { 
                border-radius: 10px; 
                border: 1px solid #ffb7b2; 
            }
            
            /* Expander（折りたたみ）のデザイン */
            details {
                border: 1px solid #ffb7b2;
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 0.6);
                margin-bottom: 10px;
            }
            
            /* メインカード */
            .main-card {
                background-color: rgba(255, 255, 255, 0.9);
                padding: 30px;
                border-radius: 20px;
                border: 2px solid #ffb7b2;
                text-align: center;
                margin-bottom: 25px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.05);
            }
            
            /* ボタンデザイン */
            .stButton>button {
                width: 100%; border-radius: 20px; border: none;
                background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
                color: white !important;
                font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s;
            }
            .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 8px rgba(0,0,0,0.15); opacity: 0.9; }
            
            img { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            footer {visibility: hidden;}
            .block-container { padding-top: 2rem; padding-bottom: 5rem; }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================
# Wikipedia画像検索
# ==========================================
@st.cache_data(ttl=3600)
def get_wiki_image(flower_name):
    """Wikipediaから植物の画像を検索して取得する"""
    if not flower_name: return None, "名前が空です"
    
    url = "https://ja.wikipedia.org/w/api.php"
    headers = { "User-Agent": "FlowerApp/1.0" }
    
    params = { 
        "action": "query", 
        "format": "json", 
        "generator": "search", 
        "gsrsearch": f"{flower_name} 植物", 
        "gsrlimit": 1, 
        "prop": "pageimages", 
        "piprop": "original" 
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        
        for page_id in pages:
            if "original" in pages[page_id]: 
                return pages[page_id]["original"]["source"], None
    except: 
        pass
    
    return None, "画像なし"

# ==========================================
# データの読み込み
# ==========================================
@st.cache_data
def load_data():
    csv_files = glob.glob("data/*.csv")
    if not csv_files: return None
    df_list = []
    for filename in csv_files:
        try:
            try: df = pd.read_csv(filename, encoding='utf-8')
            except: df = pd.read_csv(filename, encoding='shift_jis')
            df_list.append(df)
        except: pass
    if df_list:
        return pd.concat(df_list, ignore_index=True).drop_duplicates(subset=['name']).fillna("")
    return None

df = load_data()
if df is None: st.error("データフォルダ（data）にCSVファイルが存在しません"); st.stop()
flower_data = df.to_dict('records')

# ==========================================
# お気に入り機能
# ==========================================
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

def toggle_favorite(flower_name):
    if flower_name in st.session_state.favorites:
        st.session_state.favorites.remove(flower_name)
    else:
        st.session_state.favorites.append(flower_name)

def render_fav_button(flower_name, key_suffix=""):
    is_fav = flower_name in st.session_state.favorites
    label = "🗑️ お気に入りから解除" if is_fav else "❤️ お気に入りに追加"
    st.button(label, key=f"fav_{flower_name}_{key_suffix}", on_click=toggle_favorite, args=(flower_name,))

# ==========================================
# 共通表示カード
# ==========================================
def show_flower_card(flower_row, key_suffix=""):
    """花の情報を見やすく表示するカード"""
    flower_name = flower_row['name']
    
    with st.spinner(f"画像を検索中..."):
        wiki_image, _ = get_wiki_image(flower_name)
        if wiki_image: 
            st.image(wiki_image, use_container_width=True)
            st.caption("出典: Wikipedia")
        else: 
            st.info("画像が見つかりませんでした")

    render_fav_button(flower_name, key_suffix)

    st.markdown(f"### 💌 花言葉: {flower_row['meaning']}")
    st.write(f"📅 **誕生花:** {flower_row['birth_flower']}")

    # カラムレイアウトと詳細情報の表示
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🏷️ 名前の由来", expanded=True):
            st.write(flower_row.get('name_origin', '情報なし'))
    with col2:
        with st.expander("📖 花言葉の由来", expanded=True):
            st.write(flower_row.get('meaning_origin', '情報なし'))
            
    if flower_row.get('trivia'):
        st.info(f"💡 豆知識: {flower_row['trivia']}")

# ==========================================
# サイドバー設定
# ==========================================
st.sidebar.header("🌷 花言葉図鑑")
mode = st.sidebar.radio(
    "メニュー", 
    ["本日の誕生花", "図鑑をみる", "キーワード検索", "日付で検索", "ランダム表示", "花言葉クイズ", "❤️ お気に入り"]
)
st.sidebar.divider()
show_effect = st.sidebar.checkbox("🎉 演出（紙吹雪）", value=True)

st.sidebar.divider()
# 免責事項の表示
with st.sidebar.expander("⚠️ 免責事項・ご利用上の注意"):
    st.markdown("""
    **1. 情報の正確性について**
    本アプリの情報（花言葉・由来・誕生花等）は、AIおよび一般的な文献を参考に作成されています。諸説あるため、一つのエンターテインメントとしてお楽しみください。

    **2. 著作権・画像について**
    本アプリ内の解説文は独自に生成されたものです。画像はWikipedia Commons等のライセンスに基づき引用・表示している場合があります。

    **3. 免責**
    本アプリの利用によって生じたいかなるトラブル・損害等に対しても、開発者は一切の責任を負いかねます。
    """)
    st.caption("© 2026 tkg-seimei")

# ==========================================
# 1. 本日の誕生花
# ==========================================
if mode == "本日の誕生花":
    st.header("💐 本日の誕生花")
    
    today = now_jst
    today_str = f"{today.month}月{today.day}日" 
    
    today_flowers = df[df['birth_flower'].astype(str).str.contains(today_str, na=False)]
    
    if not today_flowers.empty:
        f = today_flowers.iloc[0]
        st.markdown(f"""
        <div class="main-card">
            <h2 style="color: #F63366;">{today_str}</h2>
            <p>今日の誕生花は...</p>
            <h1 style="font-size: 3em; margin: 10px 0;">{f['name']}</h1>
            <h3 style="background: #fff0f5; display: inline-block; padding: 5px 20px; border-radius: 50px;">
                花言葉: {f['meaning']}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        show_flower_card(f, "today")
    else:
        st.markdown(f"""
        <div class="main-card" style="border-color: #ccc;">
            <h2 style="color: #888;">📅 {today_str}</h2>
            <p style="font-weight: bold; color: #666;">今日の誕生花は登録されていません。</p>
            <hr style="border: 0; border-top: 1px dashed #ccc; margin: 20px 0;">
            <p style="color: #888;">代わりに、こちらの花はいかがですか？</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'daily_alt_flower' not in st.session_state:
            st.session_state.daily_alt_flower = random.choice(flower_data)
        alt = st.session_state.daily_alt_flower
        
        st.subheader(f"✨ おすすめの花: {alt['name']}")
        show_flower_card(alt, "alt_today")

# ==========================================
# 2. 図鑑をみる
# ==========================================
elif mode == "図鑑をみる":
    st.header("📖 植物図鑑")
    flower_names = sorted([f["name"] for f in flower_data])
    selected_name = st.selectbox("調べたい植物を選んでください", ["-- 選択してください --"] + flower_names)
    
    if selected_name != "-- 選択してください --":
        f = next((item for item in flower_data if item["name"] == selected_name), None)
        if f:
            st.divider()
            st.header(f['name'])
            show_flower_card(f, "catalog")

# ==========================================
# 3. キーワード検索
# ==========================================
elif mode == "キーワード検索":
    st.header("🔍 キーワード検索")
    st.write("人気のテーマ:")
    cols = st.columns(4)
    keywords = ["愛", "感謝", "希望", "幸福"]
    if 'search_q' not in st.session_state: st.session_state.search_q = ""
    for i, kw in enumerate(keywords):
        if cols[i].button(kw, use_container_width=True):
            st.session_state.search_q = kw
            
    query = st.text_input("花の名前や花言葉から検索できます", key='search_q', placeholder="例：バラ、ピンク")
    
    if query:
        results = df[
            df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
        ]
        st.write(f"🔍 **{len(results)}** 件見つかりました")
        
        for _, row in results.iterrows():
            with st.expander(f"🌸 {row['name']} （{row['meaning']}）"):
                show_flower_card(row, f"search_{row['name']}")

# ==========================================
# 4. 日付で検索
# ==========================================
elif mode == "日付で検索":
    st.header("📅 日付で検索")
    st.write("誕生日や記念日の花を調べられます。")
    
    search_date = st.date_input("日付を選択してください", value=now_jst)
    
    if search_date:
        s_str = f"{search_date.month}月{search_date.day}日"
        date_results = df[df['birth_flower'].astype(str).str.contains(s_str, na=False)]
        
        if not date_results.empty:
            st.success(f"✨ {s_str} の誕生花は {len(date_results)}件 です")
            for _, row in date_results.iterrows():
                st.divider()
                st.subheader(row['name'])
                show_flower_card(row, f"date_{row['name']}")
        else:
            st.warning(f"{s_str} の誕生花は登録されていません。")

# ==========================================
# 5. ランダム表示
# ==========================================
elif mode == "ランダム表示":
    st.header("🔀 ランダム表示")
    if 'random_flower' not in st.session_state:
        st.session_state.random_flower = None

    if st.button("花を引く", type="primary", use_container_width=True):
        st.session_state.random_flower = random.choice(flower_data)

    if st.session_state.random_flower:
        flower = st.session_state.random_flower
        st.divider()
        st.header(flower['name'])
        show_flower_card(flower, "random")

# ==========================================
# 6. 花言葉クイズ
# ==========================================
elif mode == "花言葉クイズ":
    st.header("❓ 花言葉クイズ")
    quiz_type = st.radio("出題モード", ["言葉から名前を当てる", "名前（写真）から言葉を当てる"], horizontal=True)
    st.divider()

    if "q_data" not in st.session_state:
        st.session_state.q_data = random.choice(flower_data)
        st.session_state.ans_view = False
    
    q = st.session_state.q_data
    
    if quiz_type == "言葉から名前を当てる":
        st.info(f"この花言葉を持つ植物は何でしょう？\n\n## 「{q['meaning']}」")
        if st.checkbox("💡 写真をヒントに見る"):
            with st.spinner("ヒント画像を検索中..."):
                wiki_image, _ = get_wiki_image(q['name'])
                if wiki_image: st.image(wiki_image, width=300)
                else: st.warning("ヒント画像がありませんでした")

    else:
        st.info(f"この植物の花言葉は何でしょう？\n\n## **{q['name']}**")
        with st.spinner("画像を検索中..."):
            wiki_image, _ = get_wiki_image(q['name'])
            if wiki_image: st.image(wiki_image, width=300)
            st.caption("出典: Wikipedia")

    st.write("")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("答えを見る", type="primary", use_container_width=True):
            st.session_state.ans_view = True
    with col_q2:
        if st.button("次の問題へ", use_container_width=True):
            st.session_state.q_data = random.choice(flower_data)
            st.session_state.ans_view = False
            st.rerun()

    if st.session_state.ans_view:
        if show_effect: st.balloons()
        st.divider()
        st.success(f"正解は... **{q['name']}** （花言葉：{q['meaning']}） でした！")
        
        with st.expander("📖 解説を読む", expanded=True):
             st.write(f"**由来:** {q.get('meaning_origin', '')}")
             st.write(f"**名前の由来:** {q.get('name_origin', '')}")

# ==========================================
# 7. お気に入り一覧
# ==========================================
elif mode == "❤️ お気に入り":
    st.header("❤️ お気に入りリスト")
    fav_list = st.session_state.favorites
    
    if not fav_list:
        st.info("まだお気に入りがありません。")
    else:
        st.write(f"**{len(fav_list)}** 件保存しています")
        fav_flowers = df[df['name'].isin(fav_list)]
        
        for index, row in fav_flowers.iterrows():
            with st.container():
                st.divider()
                st.subheader(row['name'])
                show_flower_card(row, f"fav_page_{row['name']}")
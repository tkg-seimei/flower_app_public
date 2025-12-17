import streamlit as st
import pandas as pd
import glob
import os
import random
import requests

# --- ページ設定 ---
st.set_page_config(
    page_title="花言葉図鑑",
    page_icon="🌷",
    layout="centered"
)

# ==========================================
# ✨ デザイン調整（脱・チープ化）
# ==========================================
hide_streamlit_style = """
            <style>
            /* 右上のデプロイボタンなどを隠す */
            .stDeployButton {display:none;}
            /* 下のMade with Streamlitを隠す */
            footer {visibility: hidden;}
            /* 右上のハンバーガーメニューを隠す（必要なら消してください） */
            #MainMenu {visibility: hidden;}
            /* 全体の余白を調整してスマホで見やすく */
            .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# タイトル
st.header("💐 花言葉図鑑")

# ==========================================
# 免責事項
# ==========================================
st.sidebar.info("※このアプリは個人の学習用に作成されたものです。情報の正確性を保証するものではありません。")

# デバッグ用スイッチ
is_debug = st.sidebar.checkbox("デバッグモード", value=False)

# --- Wikipedia画像検索関数 ---
@st.cache_data(ttl=3600)
def get_wiki_image(flower_name):
    if not flower_name:
        return None, "名前が空です"
    url = "https://ja.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "FlowerApp/1.0 (streamlit-app-learning)"
    }
    search_query = f"{flower_name} 植物"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",       
        "gsrsearch": search_query,   
        "gsrlimit": 1,               
        "prop": "pageimages",        
        "piprop": "original"         
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status() 
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        if not pages:
            params["gsrsearch"] = flower_name
            response = requests.get(url, params=params, headers=headers, timeout=5)
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
        if not pages:
             return None, "検索結果が0件でした"
        for page_id in pages:
            if "original" in pages[page_id]:
                return pages[page_id]["original"]["source"], None
            else:
                return None, "画像が見つかりませんでした"
    except Exception as e:
        return None, f"通信エラー: {e}"
    return None, "不明なエラー"

# --- データの読み込み ---
@st.cache_data
def load_data():
    csv_files = glob.glob("data/*.csv")
    if not csv_files:
        return None
    df_list = []
    for filename in csv_files:
        try:
            try:
                df = pd.read_csv(filename, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(filename, encoding='shift_jis')
                except:
                    df = pd.read_csv(filename, encoding='cp932')
            df_list.append(df)
        except Exception as e:
            st.warning(f"CSV読込エラー: {filename} - {e}")
    if df_list:
        final_df = pd.concat(df_list, ignore_index=True)
        final_df = final_df.drop_duplicates(subset=['name'], keep='first')
        final_df = final_df.fillna("")
        return final_df
    else:
        return None

df = load_data()
if df is None:
    st.error("データがありません。")
    st.stop()
flower_data = df.to_dict('records')

# --- メニュー ---
st.sidebar.header("メニュー")
mode = st.sidebar.radio("モード選択", ["図鑑一覧", "キーワード検索", "ランダム表示", "花言葉クイズ"])

# --- 画像表示関数 ---
def show_flower_image_smart(flower_row):
    flower_name = flower_row.get("name")
    with st.spinner(f"画像を検索中..."):
        wiki_image, error_msg = get_wiki_image(flower_name)
        if wiki_image:
            st.image(wiki_image, use_container_width=True)
            st.caption("出典: Wikipedia")
        else:
            st.info("画像なし")
            if is_debug:
                st.error(f"【デバッグ】原因: {error_msg}")

# --- メイン機能 ---

# A. 図鑑一覧
if mode == "図鑑一覧":
    st.subheader("📖 植物一覧")
    flower_names = sorted([f["name"] for f in flower_data])
    selected_name = st.sidebar.selectbox("植物を選択", flower_names)
    target_flower = next((f for f in flower_data if f["name"] == selected_name), None)
    
    if target_flower:
        st.divider()
        st.header(target_flower['name'])
        show_flower_image_smart(target_flower)
        st.write("") 
        st.subheader("基本情報")
        st.write(f"**花言葉:** {target_flower['meaning']}")
        st.write(f"**誕生花:** {target_flower['birth_flower']}")
        
        with st.expander("詳細情報"):
            st.write(f"**由来:** {target_flower['name_origin']}")
            st.write(f"**花言葉の由来:** {target_flower['meaning_origin']}")
            st.info(f"**豆知識:** {target_flower['trivia']}")

# B. キーワード検索
elif mode == "キーワード検索":
    st.subheader("🔍 検索")
    query = st.sidebar.text_input("検索語句", placeholder="名前、花言葉...")
    if query:
        results = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)]
        st.write(f"検索結果: **{len(results)}** 件")
        for index, row in results.iterrows():
            with st.container():
                st.divider()
                st.subheader(row['name'])
                st.write(f"**花言葉**: {row['meaning']}")
                with st.expander("画像と詳細を見る"):
                    show_flower_image_smart(row)
                    st.write(f"**由来:** {row['meaning_origin']}")
                    if row['trivia']:
                        st.info(row['trivia'])

# C. ランダム表示
elif mode == "ランダム表示":
    st.subheader("🔀 ランダム表示")
    if 'random_flower' not in st.session_state:
        st.session_state.random_flower = None
    if st.button("花を引く", type="primary", use_container_width=True):
        st.session_state.random_flower = random.choice(flower_data)
    if st.session_state.random_flower:
        flower = st.session_state.random_flower
        st.divider()
        st.header(flower['name'])
        show_flower_image_smart(flower)
        st.subheader(f"花言葉: 「{flower['meaning']}」")
        st.write(f"**誕生花:** {flower['birth_flower']}")
        with st.expander("詳細情報", expanded=True):
            st.write(f"**由来:** {flower['name_origin']}")
            st.write(f"**花言葉の由来:** {flower['meaning_origin']}")
            st.info(f"**豆知識:** {flower['trivia']}")

# D. クイズ
elif mode == "花言葉クイズ":
    st.subheader("❓ 花言葉クイズ")
    if "quiz_flower" not in st.session_state:
        st.session_state.quiz_flower = None
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False
    def next_question():
        st.session_state.quiz_flower = random.choice(flower_data)
        st.session_state.show_answer = False
    def open_answer():
        st.session_state.show_answer = True
    if st.session_state.quiz_flower is None:
        next_question()
    q = st.session_state.quiz_flower
    st.info(f"この花言葉を持つ植物は？\n\n### {q['meaning']}")
    with st.expander("ヒント"):
        st.write(q['trivia'])
    st.write("") 
    col_a, col_b = st.columns(2)
    with col_a:
        st.button("回答", on_click=open_answer, type="primary", use_container_width=True)
    with col_b:
        st.button("次へ", on_click=next_question, use_container_width=True)
    st.divider()
    if st.session_state.show_answer:
        st.success(f"正解: **{q['name']}**")
        show_flower_image_smart(q)
        st.markdown("**由来**")
        st.write(q['meaning_origin'])
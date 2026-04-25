import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os

# === КОНФИГУРАЦИЯ СТРАНИЦЫ ===
st.set_page_config(
    page_title="Zahratun Jondor-1",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === КАСТОМНЫЕ СТИЛИ ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0d0d0d;
        color: #f0f0f0;
    }
    .stApp { background-color: #0d0d0d; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #111 100%);
        border-right: 1px solid #2a2a2a;
    }

    .metric-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: #FF4B4B; }
    .metric-label { font-size: 0.75em; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-family: 'Bebas Neue', sans-serif; font-size: 2.2em; color: #fff; margin: 4px 0; }
    .metric-delta-pos { font-size: 0.85em; color: #4CAF50; }
    .metric-delta-neg { font-size: 0.85em; color: #FF4B4B; }

    .section-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2em;
        color: #FF4B4B;
        letter-spacing: 2px;
        margin-bottom: 0;
    }
    .section-sub { color: #666; font-size: 0.85em; margin-top: -4px; }

    div[data-testid="stRadio"] label {
        color: #aaa !important;
        font-size: 0.9em;
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        color: #FF4B4B !important;
        font-weight: 600;
    }

    .stCodeBlock { border-radius: 10px; }
    hr { border-color: #2a2a2a; }
</style>
""", unsafe_allow_html=True)

# === CREDENTIALS — через st.secrets или .env ===
# Создай файл .streamlit/secrets.toml:
# [iiko]
# ip = "192.168.1.100"
# login = "admin"
# password = "yourpass"
IIKO_IP    = st.secrets.get("iiko", {}).get("ip",       os.getenv("IIKO_IP",    ""))
IIKO_LOGIN = st.secrets.get("iiko", {}).get("login",    os.getenv("IIKO_LOGIN", ""))
IIKO_PASS  = st.secrets.get("iiko", {}).get("password", os.getenv("IIKO_PASS",  ""))

# === ДАННЫЕ: реальный iiko или демо ===
@st.cache_data(ttl=300)
def get_iiko_data():
    if IIKO_IP and IIKO_LOGIN and IIKO_PASS:
        try:
            # --- Авторизация в iiko ---
            auth_url = f"http://{IIKO_IP}/resto/api/auth"
            r = requests.get(auth_url, params={"login": IIKO_LOGIN, "pass": IIKO_PASS}, timeout=8)
            r.raise_for_status()
            token = r.text.strip()

            # --- Получение продаж (пример endpoint) ---
            sales_url = f"http://{IIKO_IP}/resto/api/v2/reports/olap"
            # Здесь настрой свой запрос под нужный отчёт iiko
            # r2 = requests.post(sales_url, headers={"Cookie": f"key={token}"}, json={...})

            # Пока возвращаем демо — замени на r2.json() после настройки
            st.sidebar.success("🟢 iiko подключён")
        except requests.exceptions.ConnectionError:
            st.sidebar.warning("⚠️ iiko недоступен — демо-режим")
        except Exception as e:
            st.sidebar.warning(f"⚠️ Ошибка: {e}")
    else:
        st.sidebar.info("ℹ️ Демо-режим (нет credentials)")

    # Демо-данные (замени на реальные после подключения)
    return pd.DataFrame({
        'Категория': ['Бургеры', 'Напитки', 'Фри', 'Соусы', 'Доставка'],
        'Выручка':   [450000, 120000, 95000, 30000, 300000],
        'Количество':[150, 200, 180, 210, 45]
    })

df = get_iiko_data()

# === БОКОВАЯ ПАНЕЛЬ ===
st.sidebar.markdown("""
    <div style="text-align:center; padding: 10px 0 20px;">
        <div style="font-family:'Bebas Neue',sans-serif; font-size:2em; color:#FF4B4B; letter-spacing:3px;">ZAHRATUN</div>
        <div style="font-size:0.8em; color:#555;">Филиал · Jondor-1</div>
    </div>
    <hr style="border-color:#2a2a2a; margin-bottom:20px;">
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "НАВИГАЦИЯ",
    ["📊 Общая сводка", "🚴 Доставка vs Зал", "📉 ABC-анализ", "🤖 Для NotebookLM"]
)

# === УТИЛИТЫ ===
def fmt(n): return f"{n:,.0f}".replace(",", " ")

# ============================================================
# 📊 ОБЩАЯ СВОДКА
# ============================================================
if menu == "📊 Общая сводка":
    st.markdown('<div class="section-title">ОПЕРАТИВНЫЙ ОТЧЁТ</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Zahratun Jondor-1 · Сегодня</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    total_rev   = df['Выручка'].sum()
    total_cnt   = df['Количество'].sum()
    avg_check   = total_rev / total_cnt if total_cnt else 0

    c1, c2, c3 = st.columns(3)
    cards = [
        (c1, "Выручка", f"{fmt(total_rev)} сум", "+15%", True),
        (c2, "Средний чек", f"{fmt(avg_check)} сум", "+3%", True),
        (c3, "Чеков", f"{total_cnt}", "+10%", True),
    ]
    for col, label, value, delta, pos in cards:
        with col:
            color_class = "metric-delta-pos" if pos else "metric-delta-neg"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="{color_class}">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_pie, col_bar = st.columns([1, 1])
    with col_pie:
        fig_pie = px.pie(
            df, values='Выручка', names='Категория',
            title="Доля выручки по категориям", hole=0.5,
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#aaa', title_font_color='#fff'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        fig_bar = px.bar(
            df, x='Категория', y='Выручка',
            title="Выручка по категориям (сум)",
            color='Выручка', color_continuous_scale='Reds'
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#aaa', title_font_color='#fff',
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, gridcolor='#2a2a2a'),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ============================================================
# 🚴 ДОСТАВКА vs ЗАЛ
# ============================================================
elif menu == "🚴 Доставка vs Зал":
    st.markdown('<div class="section-title">ДОСТАВКА vs ЗАЛ</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Сравнение каналов продаж</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    delivery = int(df[df['Категория'] == 'Доставка']['Выручка'].values[0]) if 'Доставка' in df['Категория'].values else 0
    hall     = df['Выручка'].sum() - delivery
    total    = hall + delivery

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="border-color:#FF4B4B;">
            <div class="metric-label">🏠 Зал</div>
            <div class="metric-value">{fmt(hall)}</div>
            <div style="color:#888; font-size:0.8em;">{hall/total*100:.1f}% от общего</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="border-color:#FF4B4B;">
            <div class="metric-label">🛵 Доставка</div>
            <div class="metric-value">{fmt(delivery)}</div>
            <div style="color:#888; font-size:0.8em;">{delivery/total*100:.1f}% от общего</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    fig = go.Figure(go.Bar(
        x=['Зал', 'Доставка'], y=[hall, delivery],
        marker_color=['#FF4B4B', '#ff8c8c'],
        text=[fmt(hall), fmt(delivery)], textposition='outside',
        textfont_color='#aaa'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#aaa', title_font_color='#fff',
        yaxis=dict(showgrid=False), xaxis=dict(showgrid=False),
        showlegend=False, height=350
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 📉 ABC-АНАЛИЗ
# ============================================================
elif menu == "📉 ABC-анализ":
    st.markdown('<div class="section-title">ABC-АНАЛИЗ</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Классификация категорий по выручке</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    abc = df.copy().sort_values('Выручка', ascending=False)
    abc['Доля %']       = (abc['Выручка'] / abc['Выручка'].sum() * 100).round(1)
    abc['Накопленно %'] = abc['Доля %'].cumsum().round(1)

    def abc_class(cum):
        if cum <= 80:  return 'A'
        if cum <= 95:  return 'B'
        return 'C'
    abc['Класс'] = abc['Накопленно %'].apply(abc_class)

    color_map = {'A': '#4CAF50', 'B': '#FF9800', 'C': '#FF4B4B'}

    col_t, col_c = st.columns([3, 1])
    with col_t:
        st.dataframe(
            abc[['Категория', 'Выручка', 'Доля %', 'Накопленно %', 'Класс']]
              .style.applymap(lambda v: f"color:{color_map.get(v,'#fff')};font-weight:bold", subset=['Класс']),
            use_container_width=True, hide_index=True
        )
    with col_c:
        for cls, clr in color_map.items():
            items = abc[abc['Класс'] == cls]['Категория'].tolist()
            st.markdown(f"""
            <div style="background:#1a1a1a;border:1px solid {clr};border-radius:8px;padding:12px;margin-bottom:10px;">
                <div style="color:{clr};font-weight:bold;font-size:1.2em;">Класс {cls}</div>
                <div style="color:#aaa;font-size:0.85em;">{', '.join(items) if items else '—'}</div>
            </div>""", unsafe_allow_html=True)

    fig_abc = px.bar(
        abc, x='Категория', y='Выручка', color='Класс',
        color_discrete_map=color_map, title="Распределение по ABC"
    )
    fig_abc.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#aaa', title_font_color='#fff',
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_abc, use_container_width=True)

# ============================================================
# 🤖 ДЛЯ NOTEBOOKLM
# ============================================================
elif menu == "🤖 Для NotebookLM":
    st.markdown('<div class="section-title">АНАЛИТИКА ДЛЯ ИИ</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Скопируй и вставь в NotebookLM</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    top_cat  = df.loc[df['Выручка'].idxmax(), 'Категория']
    low_cat  = df.loc[df['Выручка'].idxmin(), 'Категория']
    total    = df['Выручка'].sum()
    avg_chk  = total / df['Количество'].sum()

    summary = f"""
ОТЧЁТ: ZAHRATUN JONDOR-1
=========================
Период: текущая неделя
Общая выручка:  {fmt(total)} сум
Средний чек:    {fmt(avg_chk)} сум
Всего чеков:    {df['Количество'].sum()}

ТОП категория:  {top_cat} ({fmt(df[df['Категория']==top_cat]['Выручка'].values[0])} сум)
Слабая зона:    {low_cat} ({fmt(df[df['Категория']==low_cat]['Выручка'].values[0])} сум)

ДАННЫЕ ПО КАТЕГОРИЯМ:
{df[['Категория','Выручка','Количество']].to_string(index=False)}

ABC-АНАЛИЗ:
A — приоритетные категории (>80% выручки)
B — вторичные (80–95%)
C — аутсайдеры (<5%)

ЗАДАЧА ДЛЯ ИИ:
1. Проанализируй данные и найди узкие места.
2. Предложи 3 способа поднять продажи категории '{low_cat}'.
3. Как увеличить долю доставки не теряя качества зала?
"""
    st.code(summary, language="text")
    st.download_button("⬇️ Скачать как .txt", summary, file_name="zahratun_report.txt", mime="text/plain")

# === ПОДВАЛ ===
st.sidebar.markdown("---")
st.sidebar.markdown('<div style="color:#444; font-size:0.75em; text-align:center;">Zahratun · iiko Dashboard v2.0</div>', unsafe_allow_html=True)

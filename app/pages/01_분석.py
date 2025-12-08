import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# 페이지 기본 설정
# =========================
st.set_page_config(page_title="공공화장실 데이터맵 | 분석", layout="wide")

# =========================
# 글로벌 스타일
# =========================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main { background-color: #FAFAFB !important; }
header[data-testid="stHeader"] { display: none !important; }
[data-testid="stAppViewContainer"] .main .block-container, .stMainBlockContainer { padding: 0 32px; max-width: 1200px; margin-bottom: 0; }
.stHorizontalBlock { gap: 20px; }
h1, h2, h3, h4, label, div, span { font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif; color: #222222; }

/* 상단 메트릭 카드 */
.analytics-card {
  background-color: #FFFFFF; border-radius: 24px; padding: 20px 24px 18px;
  box-shadow: 0 10px 30px rgba(23, 34, 59, 0.06); height: 135px;
  display: flex; flex-direction: column; justify-content: space-between; overflow: hidden;
}
.metric-label { font-size: 14px; color: #374151; }
.metric-value { font-size: 30px; font-weight: 700; color: #222222; margin-top: 4px; }
.metric-sub { margin-top: 4px; font-size: 13px; color: #9FA8BA; display: flex; align-items: center; gap: 4px; }

/* Plotly */
.js-plotly-plot .plotly .main-svg { background-color: rgba(0,0,0,0) !important; overflow: visible !important; }
.infolayer .g-gdata .g-t .text { fill: #222222 !important; }
.rect.nsewdrag.drag { pointer-events: none !important; opacity: 0 !important; }

/* 상단 우측 구 선택 */
div[data-testid="stSelectbox"] { width: 150px; margin-left: auto; margin-top: 0; margin-bottom: 0; }
div[data-testid="stSelectbox"] > label { display: none !important; }
div[data-testid="stSelectbox"] > div {
  background-color: #FFFFFF; border-radius: 16px; padding: 14px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06); height: 45px; display: flex; align-items: center; box-sizing: border-box;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] { font-size: 16px; font-weight: 600; color: #3F3D56; }
div[data-testid="stSelectbox"] [data-baseweb="select"] > div { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }
div[data-testid="stSelectbox"] [data-baseweb="select"] div[role="combobox"] { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
div[data-testid="stSelectbox"] svg { color: #8F8F99; width: 20px; height: 20px; }
</style>
""", unsafe_allow_html=True)

# =========================
# 안전 로드/표준화 유틸
# =========================
@st.cache_data
def _read_csv_safe(paths: list[str]) -> pd.DataFrame | None:
    for p in paths:
        try:
            return pd.read_csv(p, encoding="utf-8-sig")
        except Exception:
            try:
                return pd.read_csv(p, encoding="cp949")
            except Exception:
                continue
    return None

def _standardize_toilets(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None or df.empty:
        return None
    if "lon" in df.columns and "lng" not in df.columns:
        df = df.rename(columns={"lon": "lng"})
    if "longitude" in df.columns and "lng" not in df.columns:
        df = df.rename(columns={"longitude": "lng"})
    if "latitude" in df.columns and "lat" not in df.columns:
        df = df.rename(columns={"latitude": "lat"})
    for c in ["lat", "lng"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["accessible", "male_wc", "female_wc"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    df = df.dropna(subset=["lat", "lng"])
    return df

# =========================
# 데이터 로드
# =========================
@st.cache_data
def load_dataset():
    toilets_app = _read_csv_safe(["data/app/toilets_app.csv"])
    pop_app     = _read_csv_safe(["data/app/population_app.csv"])

    toilets_app = _standardize_toilets(toilets_app)

    for df in (toilets_app, pop_app):
        df["district"] = df["district"].astype(str).str.strip()
        df["dong"]     = df["dong"].astype(str).str.strip()

    # 인구/면적/밀도 숫자화
    pop_app["population"] = pd.to_numeric(pop_app["population"], errors="coerce").fillna(0).astype(int)
    for c in ["area_km2", "pop_density_km2"]:
        if c in pop_app.columns:
            pop_app[c] = pd.to_numeric(pop_app[c], errors="coerce")

    # 다른 구가 없으면 베이스라인 병합
    curr_districts = set(str(d) for d in pop_app["district"].dropna().unique())
    if len(curr_districts) <= 1:
        base_toilets = _read_csv_safe(["data/baseline_toilets_mock.csv"])
        base_pop     = _read_csv_safe(["data/baseline_population_mock.csv"])
        base_toilets = _standardize_toilets(base_toilets)
        if base_pop is not None:
            base_pop["population"] = pd.to_numeric(base_pop["population"], errors="coerce").fillna(0).astype(int)
        if base_toilets is not None and not base_toilets.empty:
            toilets_app = pd.concat([toilets_app, base_toilets], ignore_index=True)
        if base_pop is not None and not base_pop.empty:
            pop_app = pd.concat([pop_app, base_pop], ignore_index=True)

    # 동별 집계
    toilets_app["bowls_sum"] = (
        pd.to_numeric(toilets_app.get("male_wc", 0), errors="coerce").fillna(0) +
        pd.to_numeric(toilets_app.get("female_wc", 0), errors="coerce").fillna(0)
    )
    by = toilets_app.groupby(["district", "dong"], as_index=False).agg(
        toilets_count=("toilet_id", "count"),
        accessible_count=("accessible", "sum"),
        bowls_total=("bowls_sum", "sum"),
    )

    # 병합 컬럼 확장
    merge_cols = ["district", "dong", "population"]
    for c in ["area_km2", "pop_density_km2"]:
        if c in pop_app.columns:
            merge_cols.append(c)

    agg = by.merge(pop_app[merge_cols], on=["district", "dong"], how="left")

    # 파생 지표
    agg["population"] = pd.to_numeric(agg["population"], errors="coerce").fillna(0).astype(int)
    agg["toilets_per_1k"] = np.where(agg["population"] > 0, agg["toilets_count"] / agg["population"] * 1000.0, np.nan)
    agg["accessible_ratio"] = np.where(agg["toilets_count"] > 0, agg["accessible_count"] / agg["toilets_count"], np.nan)

    # 면적당 화장실 수
    if "area_km2" in agg.columns:
        agg["area_km2"] = pd.to_numeric(agg["area_km2"], errors="coerce")
        agg["toilets_per_km2"] = np.where(agg["area_km2"] > 0, agg["toilets_count"] / agg["area_km2"], np.nan)
    else:
        agg["toilets_per_km2"] = np.nan

    bowls_avg_all = toilets_app["bowls_sum"].replace(0, np.nan).mean()
    return toilets_app, agg, bowls_avg_all

toilets_app, agg, bowls_avg_all = load_dataset()
if agg.empty:
    st.stop()

# =========================
# 구 선택 및 선택 UI
# =========================
gu_list = sorted(agg["district"].dropna().unique())
default_index = gu_list.index("남구") if "남구" in gu_list else 0

left_spacer, right_box = st.columns([4, 1])
with right_box:
    st.markdown('<div class="gu-select-row"><div class="gu-select-card">', unsafe_allow_html=True)
    selected_gu = st.selectbox("", options=gu_list, index=default_index, label_visibility="collapsed", key="gu_select_top")
    st.markdown('</div></div>', unsafe_allow_html=True)

# =========================
# 포맷/증감 유틸 (심볼만 색상 적용)
# =========================
def fmt_int(x): return f"{int(x):,}" if pd.notna(x) else "N/A"
def fmt_pct(x): return f"{x*100:.1f}%" if pd.notna(x) else "N/A"

def delta_pp(sel, oth, thresh=2.0):
    if not (pd.notna(sel) and pd.notna(oth)): return "비교 불가"
    diff_pp = (sel - oth) * 100.0
    if abs(diff_pp) < thresh: return "⎯ 평균 수준 유지"
    
    # [수정] 기호(▲/▼)에만 색상을 적용, 숫자는 span 밖으로 뺌
    symbol = '▲' if diff_pp > 0 else '▼'
    color = '#BFA9F2' if diff_pp > 0 else '#8FDAC8'
    return f'평균 대비 <span style="color:{color}">{symbol}</span> {abs(diff_pp):.1f}%p'

def delta_pct(sel, oth, thresh=2.0):
    if not (pd.notna(sel) and pd.notna(oth)) or oth == 0: return "비교 불가"
    diff = (sel - oth) / oth * 100.0
    if abs(diff) < thresh: return "⎯ 평균 수준 유지"
    
    # [수정] 기호(▲/▼)에만 색상을 적용, 숫자는 span 밖으로 뺌
    symbol = '▲' if diff > 0 else '▼'
    color = '#BFA9F2' if diff > 0 else '#8FDAC8'
    return f'평균 대비 <span style="color:{color}">{symbol}</span> {abs(diff):.1f}%'

def bowls_avg_for_district(toi_df, district):
    df = toi_df[toi_df["district"] == district]
    if df.empty or not {"male_wc","female_wc"}.issubset(df.columns): return np.nan
    bowls = (pd.to_numeric(df["male_wc"], errors="coerce").fillna(0) + pd.to_numeric(df["female_wc"], errors="coerce").fillna(0)).replace(0, np.nan)
    return bowls.mean()

def district_metrics(agg_df, district):
    sub = agg_df[agg_df["district"] == district]
    t = int(sub["toilets_count"].sum())
    acc = int(sub["accessible_count"].sum())
    pop = int(sub["population"].sum())
    return {"toilets": t, "acc_ratio": (acc/t) if t>0 else np.nan, "per_1k": (t/pop*1000.0) if pop>0 else np.nan, "one_over_N": (pop/t) if t>0 else np.nan}

def others_average(agg_df, toi_df, selected):
    others = agg_df[agg_df["district"] != selected]
    if others.empty: return {"toilets":np.nan,"acc_ratio":np.nan,"per_1k":np.nan,"bowls_avg":np.nan}
    grp = others.groupby("district", as_index=False).agg(t=("toilets_count","sum"), acc=("accessible_count","sum"), pop=("population","sum"))
    grp["acc_ratio"] = np.where(grp["t"]>0, grp["acc"]/grp["t"], np.nan)
    grp["per_1k"] = np.where(grp["pop"]>0, grp["t"]/grp["pop"]*1000.0, np.nan)
    
    bowls_avg_others = np.nan
    if toi_df is not None and not toi_df.empty and {"district","male_wc","female_wc"}.issubset(toi_df.columns):
        b = toi_df.assign(male_wc=pd.to_numeric(toi_df["male_wc"],errors="coerce").fillna(0), female_wc=pd.to_numeric(toi_df["female_wc"],errors="coerce").fillna(0))
        b["bowls"] = (b["male_wc"]+b["female_wc"]).replace(0,np.nan)
        bowls_avg_others = b.groupby("district")["bowls"].mean().reindex(grp["district"]).mean(skipna=True)
        
    return {"toilets":grp["t"].mean(), "acc_ratio":grp["acc_ratio"].mean(), "per_1k":grp["per_1k"].mean(), "bowls_avg":bowls_avg_others}

# =========================
# 상단 요약 카드
# =========================
HAS_BOWLS = not toilets_app.empty and {"male_wc","female_wc"}.issubset(toilets_app.columns)

if selected_gu == "전체":
    cols = st.columns(4 if HAS_BOWLS else 3)
    with cols[0]:
        total = int(agg["toilets_count"].sum())
        st.markdown(f'<div class="analytics-card"><div class="metric-label">총 화장실 수</div><div class="metric-value">{fmt_int(total)}</div><div class="metric-sub">비교 불가</div></div>', unsafe_allow_html=True)
    with cols[1]:
        acc = int(agg["accessible_count"].sum())
        tot = int(agg["toilets_count"].sum())
        st.markdown(f'<div class="analytics-card"><div class="metric-label">장애인 화장실 비율</div><div class="metric-value">{fmt_pct(acc/tot if tot>0 else 0)}</div><div class="metric-sub">비교 불가</div></div>', unsafe_allow_html=True)
    if HAS_BOWLS:
        with cols[2]:
            st.markdown(f'<div class="analytics-card"><div class="metric-label">화장실 당 평균 변기 수</div><div class="metric-value">{bowls_avg_all:.1f}</div><div class="metric-sub">비교 불가</div></div>', unsafe_allow_html=True)
        idx_last = 3
    else:
        idx_last = 2
    with cols[idx_last]:
        pop = int(agg["population"].sum())
        tot = int(agg["toilets_count"].sum())
        st.markdown(f'<div class="analytics-card"><div class="metric-label">인구 대비 화장실</div><div class="metric-value">{f"1 / {int(pop/tot):,}" if tot>0 else "N/A"}</div><div class="metric-sub">비교 불가</div></div>', unsafe_allow_html=True)

else:
    sel = district_metrics(agg, selected_gu)
    oth = others_average(agg, toilets_app if HAS_BOWLS else None, selected_gu)
    if HAS_BOWLS: c1,c2,c3,c4 = st.columns(4)
    else: c1,c2,c4 = st.columns(3)

    with c1: st.markdown(f'<div class="analytics-card"><div class="metric-label">총 화장실 수</div><div class="metric-value">{fmt_int(sel["toilets"])}</div><div class="metric-sub">{delta_pct(sel["toilets"], oth["toilets"])}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="analytics-card"><div class="metric-label">장애인 화장실 비율</div><div class="metric-value">{fmt_pct(sel["acc_ratio"])}</div><div class="metric-sub">{delta_pp(sel["acc_ratio"], oth["acc_ratio"])}</div></div>', unsafe_allow_html=True)
    if HAS_BOWLS:
        with c3:
             b_sel = bowls_avg_for_district(toilets_app, selected_gu)
             b_oth = oth["bowls_avg"]
             st.markdown(f'<div class="analytics-card"><div class="metric-label">화장실 당 평균 변기 수</div><div class="metric-value">{b_sel:.1f}</div><div class="metric-sub">{delta_pct(b_sel, b_oth) if pd.notna(b_sel) and pd.notna(b_oth) else "비교 불가"}</div></div>', unsafe_allow_html=True)
    with (c4 if HAS_BOWLS else c4):
        st.markdown(f'<div class="analytics-card"><div class="metric-label">인구 대비 화장실</div><div class="metric-value">{f"1 / {int(sel["one_over_N"]):,}" if pd.notna(sel["one_over_N"]) else "N/A"}</div><div class="metric-sub">{delta_pct(sel["per_1k"], oth["per_1k"])}</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# =========================
# 차트 카드/그리드 카드
# =========================
def chart_card(title: str, fig, subtitle: str | None = None, height: int = 250):
    fig_html = fig.to_html(include_plotlyjs='cdn', full_html=False)
    sub = f'<div class="chart-subtitle">{subtitle}</div>' if subtitle else ""
    card_internal_height = height + 50
    indent_px = 16

    html = f"""
<html><head><meta charset="utf-8" />
<style>
body {{ margin:0; padding:0; background:transparent; font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif; }}
.chart-card {{ background:#FFFFFF; border-radius:24px; padding:20px 24px 18px; height:{card_internal_height}px; box-sizing:border-box; }}
.chart-title {{ font-size:18px; font-weight:700; margin-bottom:10px; color:#222222; padding-left:{indent_px}px; }}
.chart-subtitle {{ font-size:13px; color:#9FA8BA; margin-bottom:8px; padding-left:{indent_px}px; }}
.js-plotly-plot .plotly .main-svg {{ background-color: rgba(0,0,0,0) !important; overflow: visible !important; }}
.infolayer .g-gdata .g-t .text {{ fill: #222222 !important; }}
.rect.nsewdrag.drag {{ pointer-events:none !important; opacity:0 !important; }}
</style></head>
<body><div class="chart-card"><div class="chart-title">{title}</div>{sub}{fig_html}</div></body></html>
"""
    components.html(html, height=card_internal_height, scrolling=False)

def ratio_card(df, height: int = 250, cols: int = 3):
    df_calc = df.dropna(subset=['toilets_per_1k']).copy()
    if not df_calc.empty:
        low_q = df_calc['toilets_per_1k'].quantile(0.33)
        high_q = df_calc['toilets_per_1k'].quantile(0.66)
    else: low_q, high_q = 0, 0

    def classify(x):
        if pd.isna(x): return '평균'
        if x <= low_q: return '부족'
        if x > high_q: return '충분'
        return '평균'

    df = df.copy()
    df['type'] = df['toilets_per_1k'].apply(classify)
    colors = {"부족":"#D6F3E7","충분":"#E7E1FF","평균":"#EEEEEE"}
    df['color'] = df['type'].map(colors)

    target_dongs = sorted(df["dong"].unique().tolist())[:6]
    card_data = []
    for dong in target_dongs:
        row = df[df['dong'] == dong]
        if not row.empty:
            r = row.iloc[0]
            value_str = f"{r['toilets_per_1k']:.2f}" if pd.notna(r['toilets_per_1k']) else "N/A"
            card_data.append({"dong": dong, "value": value_str, "color": r['color']})
        else:
            card_data.append({"dong": dong, "value": "N/A", "color": "#EEEEEE"})

    html_cards = "".join([f'<div class="pill" style="background:{it["color"]};"><span class="pill-label">{it["dong"]}</span><span class="pill-value">{it["value"]}</span></div>' for it in card_data])

    card_internal_height = height + 50
    grid_max_px = 250 
    
    # [유지] 제목/부제목 위치 조정 값
    indent_px = 4

    html = f"""
<html><head><meta charset="utf-8" />
<style>
body {{ margin:0; padding:0; background:transparent; font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif; }}
.chart-card {{ background:#FFFFFF; border-radius:24px; padding:20px 24px 18px; height:{card_internal_height}px; box-sizing:border-box; }}
.chart-title {{ font-size:18px; font-weight:700; margin-bottom:10px; color:#222222; padding-left:{indent_px}px; }}
.chart-subtitle {{ font-size:13px; color:#9FA8BA; margin-bottom:8px; padding-left:{indent_px}px; }}
.grid-wrap {{ display:flex; justify-content:center; }}
.grid-container {{ width:100%; max-width:{grid_max_px}px; display:grid; grid-template-columns: repeat({cols}, 1fr); gap:8px; margin-top:8px; margin-bottom:4px; }}
.pill {{ display:flex; flex-direction:column; align-items:center; justify-content:center; aspect-ratio:1/1; border-radius:12px; font-size:13px; font-weight:500; color:#222222; }}
.pill-label {{ font-size:13px; font-weight:500; margin-bottom:2px; }}
.pill-value {{ font-size:15px; font-weight:700; }}
.legend {{ display:flex; justify-content:center; gap:15px; margin-top:16px; font-size:12px; color:#374151; opacity:0.7; }}
.legend-item {{ display:flex; align-items:center; gap:5px; }}
.legend-color {{ width:12px; height:12px; border-radius:4px; }}
</style></head>
<body>
  <div class="chart-card">
    <div class="chart-title">인구 대비 화장실 수</div>
    <div class="chart-subtitle">1천 명당 공중화장실 수</div>
    <div class="grid-wrap">
      <div class="grid-container">{html_cards}</div>
    </div>
    <div class="legend">
      <div class="legend-item"><div class="legend-color" style="background:#D6F3E7;"></div><span>부족</span></div>
      <div class="legend-item"><div class="legend-color" style="background:#EEEEEE;"></div><span>평균</span></div>
      <div class="legend-item"><div class="legend-color" style="background:#E7E1FF;"></div><span>충분</span></div>
    </div>
  </div>
</body></html>
"""
    components.html(html, height=card_internal_height, scrolling=False)

# =========================
# 중단 3개 카드
# =========================
if selected_gu == "전체":
    base_gu = "남구" if "남구" in agg["district"].unique() else agg["district"].iloc[0]
    df_sel = agg[agg["district"] == base_gu].copy()
else:
    df_sel = agg[agg["district"] == selected_gu].copy()

colA, colB, colC = st.columns([1.2, 1.2, 1.0])

with colA:
    fig1 = px.bar(
        df_sel.sort_values("toilets_count", ascending=True),
        y="dong", x="toilets_count", orientation="h",
        text="toilets_count"
    )
    # [유지] yaxis ticksuffix 공백 추가
    fig1.update_layout(
        xaxis_title="", yaxis_title="", template="plotly_white", height=250,
        margin=dict(l=40, r=40, t=0, b=20),
        xaxis=dict(visible=False, showgrid=False, fixedrange=True),
        yaxis=dict(tickfont=dict(size=12), fixedrange=True, ticksuffix="   "),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False, bargap=0.6, dragmode=False
    )
    fig1.update_traces(marker_color='#D6F3E7', texttemplate='%{x:,}', textposition='outside', cliponaxis=False)
    chart_card("행정동별 화장실 수", fig1, height=250)

with colB:
    fig2 = px.bar(
        df_sel.sort_values("accessible_ratio", ascending=True),
        y="dong", x="accessible_ratio", orientation="h",
        text="accessible_ratio"
    )
    # [유지] yaxis ticksuffix 공백 추가
    fig2.update_layout(
        xaxis_title="", yaxis_title="", template="plotly_white", height=250,
        margin=dict(l=40, r=40, t=0, b=20),
        xaxis=dict(visible=False, showgrid=False, fixedrange=True),
        yaxis=dict(tickfont=dict(size=12), fixedrange=True, ticksuffix="   "),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False, bargap=0.6, dragmode=False
    )
    fig2.update_traces(marker_color='#E7E1FF', texttemplate='%{x:.0%}', textposition='outside', cliponaxis=False)
    chart_card("장애인 화장실 설치 비율", fig2, height=250)

with colC:
    ratio_card(df_sel, height=250, cols=3)

# =========================
# 하단 테이블 카드
# =========================
tbl = df_sel.copy().rename(columns={"dong": "행정동", "toilets_count": "총 화장실 수", "accessible_ratio": "장애인 화장실 비율", "toilets_per_1k": "인구 대비 화장실 수", "toilets_per_km2": "면적 당 화장실 수"})
tbl["장애인 화장실 비율"] = tbl["장애인 화장실 비율"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")
tbl["인구 대비 화장실 수"] = tbl["인구 대비 화장실 수"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
if "면적 당 화장실 수" in tbl.columns: tbl["면적 당 화장실 수"] = tbl["면적 당 화장실 수"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")

cols_to_show = [c for c in ["행정동", "총 화장실 수", "장애인 화장실 비율", "인구 대비 화장실 수", "면적 당 화장실 수"] if c in tbl.columns]
html_table = tbl[cols_to_show].to_html(index=False, classes="", border=0, na_rep="N/A")

table_html = f"""
<html><head><meta charset="utf-8" />
<style>
body {{ margin:0; padding:0; background:transparent; font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif; }}
.table-card {{ background:#FFFFFF; border-radius:24px; padding:20px 24px 18px; font-size:13px; height:auto; box-sizing:border-box; overflow-y:auto; }}
h3 {{ font-size:18px; font-weight:700; margin:0 0 24px 0; color:#222222; text-align:left; }}
table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
thead tr th {{ background-color:#E7E1FF; color:#374151; font-weight:600; padding:10px 12px; font-size:13px; text-align:center; position:sticky; top:0; white-space:nowrap; }}
tbody tr td {{ border-top:1px solid #F0F1F5; padding:10px 16px; font-size:13px; color:#374151; text-align:center; white-space:nowrap; }}
th:nth-child(1), td:nth-child(1) {{ width:18%; text-align:center; font-weight:700; }}
th:nth-child(2), td:nth-child(2), th:nth-child(3), td:nth-child(3), th:nth-child(4), td:nth-child(4) th:nth-child(5), td:nth-child(5) {{ width:16%; }}
</style></head>
<body><div class="table-card"><h3>공중화장실 세부 현황</h3>{html_table}</div></body></html>
"""
components.html(table_html, height=370, scrolling=True)
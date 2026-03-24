import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.decomposition import PCA
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === CSS 样式 (保持不变) ===
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    button[data-testid="stSidebarToggle"] { visibility: visible !important; opacity: 1 !important; z-index: 9999 !important; position: fixed !important; top: 15px !important; left: 15px !important; background-color: rgba(44, 44, 44, 0.9) !important; border: 1px solid #555 !important; color: white !important; border-radius: 8px !important; padding: 5px 10px !important; }
    button[data-testid="stSidebarToggle"]:hover { background-color: #4ECDC4 !important; color: black !important; transform: scale(1.1); }
    .nav-container { display: flex; justify-content: center; gap: 15px; margin-bottom: 30px; padding: 20px; background-color: #1E1E1E; border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: fit-content; margin-left: auto; margin-right: auto; position: relative; z-index: 100; }
    .nav-btn { text-decoration: none; color: white; padding: 12px 25px; border-radius: 30px; font-weight: bold; transition: all 0.3s ease; background-color: #2C2C2C; border: 1px solid #444; display: flex; align-items: center; gap: 8px; }
    .nav-btn:hover { background-color: #4ECDC4; color: #000; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(78, 205, 196, 0.4); }
    .nav-btn.active { background-color: #4ECDC4; color: #000; box-shadow: 0 5px 15px rgba(78, 205, 196, 0.4); border-color: #4ECDC4; }
    .rec-card { background-color: #262730; border-radius: 10px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #4ECDC4; box-shadow: 0 2px 5px rgba(0,0,0,0.2); transition: transform 0.2s; }
    .rec-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
    .rec-title { font-size: 1.1em; font-weight: bold; color: #fff; }
    .rec-sub { font-size: 0.85em; color: #aaa; }
    .rec-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold; color: #000; margin-top: 5px; margin-right: 5px; }
    .badge-lottery { background-color: #FF6B6B; color: white; }
    .badge-strong { background-color: #4ECDC4; color: black; }
    .badge-corrected { background-color: #FF9F43; color: white; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
</style>
<div class="nav-container">
    <a href="../Home.py" class="nav-btn">🎓 学生画像</a>
    <a href="page_2_analysis.py" class="nav-btn active">📊 智能分析</a>
    <a href="3_🏫_大学数据库.py" class="nav-btn">🏫 大学数据库</a>
    <a href="4_📝_案例训练.py" class="nav-btn">📝 案例训练</a>
</div>
""", unsafe_allow_html=True)

if 'user_data' not in st.session_state:
    st.warning("⚠️ 未检测到学生信息，请点击顶部导航栏返回第一步。")
    st.stop()

user = st.session_state.user_data
target_country = user['country']

st.set_page_config(page_title=f"Step 2: {target_country}选校分析", layout="wide")
st.title(f"📊 {target_country} 选校策略分析 (RLHF 校准版)")

major_lower = user['major'].lower()
is_cs_major = any(keyword in major_lower for keyword in ['computer', 'cs', 'science', 'data', 'ai'])

if is_cs_major:
    st.warning(f"🔥 **检测到热门专业：{user['major']}**\n\n系统已启用 **'专业优先 + 案例校准'** 模式。难度分数将根据真实录取案例动态调整。")

st.markdown(f"""
**当前申请人画像**：
- **目标国家**: {target_country}
- **目标专业**: {user['major']}
- **综合竞争力 (UCS)**: **{user['ucs']:.1f}** (硬指标：{user['hard_score']:.1f})
""")

st.divider()

csv_path = "universities.csv"
if os.path.exists(csv_path):
    all_schools_df = pd.read_csv(csv_path)
else:
    st.error("❌ 未找到数据库文件。")
    st.stop()

if '国家' in all_schools_df.columns:
    schools_df = all_schools_df[all_schools_df['国家'] == target_country].copy()
    st.info(f"🌏 已自动筛选 **{target_country}** 的大学库，共 {len(schools_df)} 所学校。")
    if '热度系数 (0-1)' not in schools_df.columns: schools_df['热度系数 (0-1)'] = 0.5
else:
    schools_df = all_schools_df.copy()

if len(schools_df) < 3:
    st.error("学校数量不足。")
    st.stop()

if st.button("🔍 开始深度匹配分析 (加载实时权重 + 案例修正)", type="primary", use_container_width=True):
    placeholder = st.empty()
    with placeholder.container():
        st.info("🧮 构建特征矩阵...")
        time.sleep(0.5)
        st.warning("🌐 应用网络热度系数...")
        time.sleep(0.5)
        st.success("📝 加载历史案例进行 RLHF 校准...")
        time.sleep(0.8)
        st.success("✅ 分析完成！")
        time.sleep(0.3)
    placeholder.empty()
    
    st.balloons()
    
    df = schools_df.copy()
    scaler = MinMaxScaler()
    
    required_cols = ['US News 排名', '录取率 (%)', '科研强度 (1-10)', '学费 (万 RMB)']
    for col in required_cols:
        if col not in df.columns: st.error(f"缺少列：{col}"); st.stop()
            
    rank_norm = 1 - scaler.fit_transform(df[['US News 排名']]).flatten()
    admit_norm = 1 - scaler.fit_transform(df[['录取率 (%)']].values.reshape(-1, 1)).flatten()
    research_norm = scaler.fit_transform(df[['科研强度 (1-10)']]).flatten()
    
    admit_rate_vals = df['录取率 (%)'].values
    nonlinear_bonus = np.zeros_like(admit_rate_vals)
    mask_elite = admit_rate_vals < 15
    nonlinear_bonus[mask_elite] = (15 - admit_rate_vals[mask_elite]) * 1.5
    nonlinear_bonus_norm = nonlinear_bonus / nonlinear_bonus.max() if nonlinear_bonus.max() > 0 else nonlinear_bonus
        
    # 权重分配
    if target_country == "英国": w_rank, w_admit, w_research, w_major = 0.30, 0.25, 0.20, 0.25; diff_mult = 1.0
    elif target_country == "加拿大": w_rank, w_admit, w_research, w_major = 0.20, 0.35, 0.15, 0.30; diff_mult = 1.1
    elif target_country == "澳洲": w_rank, w_admit, w_research, w_major = 0.20, 0.20, 0.15, 0.45; diff_mult = 0.85
    elif target_country == "中国香港": w_rank, w_admit, w_research, w_major = 0.25, 0.30, 0.15, 0.30; diff_mult = 1.15
    else: # 美国
        if is_cs_major: w_rank, w_admit, w_research, w_major = 0.10, 0.40, 0.15, 0.35; diff_mult = 1.20
        else: w_rank, w_admit, w_research, w_major = 0.20, 0.30, 0.25, 0.15; diff_mult = 1.0

    sds_base = (rank_norm * w_rank) + (admit_norm * w_admit) + (research_norm * w_research) + (nonlinear_bonus_norm * 0.15)
    
    has_major_col = 'CS 专业实力 (1-10)' in df.columns
    if has_major_col:
        major_norm = scaler.fit_transform(df[['CS 专业实力 (1-10)']]).flatten()
        sds = (sds_base * (1 - w_major)) + (major_norm * w_major)
    else:
        sds = sds_base
    
    base_sds_values = sds * 100
    
    # 1. 应用热度系数
    heat_scores = df['热度系数 (0-1)'].values
    heat_multiplier = 1.0 + (heat_scores * 0.25)
    
    if target_country == "澳洲" and is_cs_major and has_major_col:
        mask_cs_strong = (df['CS 专业实力 (1-10)'] >= 9).values
        base_adj = np.where(mask_cs_strong, 1.15, 0.85)
        df['SDS_Raw'] = base_sds_values * base_adj * heat_multiplier
    else:
        df['SDS_Raw'] = base_sds_values * diff_mult * heat_multiplier

    # 2. 【核心】应用案例修正 (RLHF)
    from utils.case_trainer import calculate_correction_factor
    
    corrections = []
    for index, row in df.iterrows():
        corr = calculate_correction_factor(row['学校名称'], row['SDS_Raw'], user['ucs'])
        corrections.append(corr)
    
    df['Correction'] = corrections
    df['SDS_Final'] = df['SDS_Raw'] + df['Correction']
    
    # 标记彩票校
    df['Is_Lottery'] = False
    if target_country in ["美国", "加拿大"]: df['Is_Lottery'] = (df['US News 排名'] <= 3) & (df['录取率 (%)'] < 10)
    elif target_country == "中国香港": df['Is_Lottery'] = (df['学校名称'].isin(["University of Hong Kong (HKU)", "Hong Kong University of Science and Technology (HKUST)"])) & (df['录取率 (%)'] < 15)
    
    ucs = user['ucs']
    effective_ucs = ucs 
    
    # 阈值
    if target_country == "加拿大": reach_gap, safety_gap = 30, 15
    elif target_country == "英国": reach_gap, safety_gap = 8, 15
    elif target_country == "澳洲": reach_gap, safety_gap = (12 if is_cs_major else 20), (20 if is_cs_major else 30)
    elif target_country == "中国香港": reach_gap, safety_gap = 10, 18
    else: reach_gap, safety_gap = (15 if is_cs_major else 12), (25 if is_cs_major else 20)
    
    def get_category(sds):
        diff = sds - effective_ucs
        if diff > reach_gap: return "🔴 冲刺校 (Reach)"
        elif diff < -safety_gap: return "🟢 保底校 (Safety)"
        else: return "🔵 匹配校 (Match)"
            
    df['建议类型'] = df['SDS_Final'].apply(get_category)
    
    # === 推荐引擎 (使用 SDS_Final) ===
    st.subheader("🌟 为您精选推荐 (Top Picks)")
    rec_cols = st.columns(3)
    categories = ["🔴 冲刺校 (Reach)", "🔵 匹配校 (Match)", "🟢 保底校 (Safety)"]
    colors = ["#FF6B6B", "#4ECDC4", "#FFE66D"]
    
    sort_col = 'CS 专业实力 (1-10)' if (is_cs_major and has_major_col) else 'US News 排名'
    sort_name = "CS 实力" if (is_cs_major and has_major_col) else "综排"
        
    for i, cat in enumerate(categories):
        subset = df[df['建议类型'] == cat].copy()
        if len(subset) > 0:
            subset_sorted = subset.nsmallest(10, sort_col) if sort_col == 'US News 排名' else subset.nlargest(10, sort_col)
            final_picks = []
            lottery_count = 0
            for _, row in subset_sorted.iterrows():
                if cat == "🔴 冲刺校 (Reach)" and row.get('Is_Lottery', False):
                    if lottery_count < 1: final_picks.append(row); lottery_count += 1
                else: final_picks.append(row)
                if len(final_picks) >= 3: break
            
            if len(final_picks) < 3:
                remaining_indices = subset_sorted.index.difference([r.name for r in final_picks])
                remaining = subset_sorted.loc[remaining_indices]
                for _, row in remaining.iterrows():
                    final_picks.append(row)
                    if len(final_picks) >= 3: break
            
            with rec_cols[i]:
                st.markdown(f"<div style='text-align:center; margin-bottom:15px;'><h3 style='color:{colors[i]}'>{cat.split()[1]}</h3><div style='font-size:0.8em; color:#888;'>按 {sort_name} 优选</div></div>", unsafe_allow_html=True)
                for row in final_picks[:3]:
                    badges = ""
                    if row.get('Is_Lottery', False): badges += '<span class="rec-badge badge-lottery">🎫 彩票校</span>'
                    
                    # 显示修正徽章
                    if abs(row['Correction']) > 2:
                        badges += f'<span class="rec-badge badge-corrected">📝 案例修正 ({row["Correction"]:+.1f})</span>'
                    
                    if has_major_col:
                        score = row['CS 专业实力 (1-10)']
                        color_badge = "#FF6B6B" if score >= 9 else "#4ECDC4" if score >= 7 else "#FFE66D"
                        badges += f'<span class="rec-badge" style="background-color:{color_badge}">CS: {score}/10</span>'
                    
                    st.markdown(f"""
                    <div class="rec-card" style="border-left-color: {colors[i]};">
                        <div class="rec-title">{row['学校名称']}</div>
                        <div class="rec-sub">排名：#{row['US News 排名']} | 录取率：{row['录取率 (%)']}%</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:5px;">
                            <div class="rec-sub" style="color:#aaa;">难度：{row['SDS_Final']:.1f}</div>
                            <div>{badges}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            with rec_cols[i]: st.info(f"暂无 {cat.split()[1]} 推荐")

    st.divider()
    
    # PCA 可视化 (使用 SDS_Final)
    features = ['US News 排名', '录取率 (%)', '科研强度 (1-10)', '学费 (万 RMB)']
    if has_major_col: features.append('CS 专业实力 (1-10)')
    pca_input = df[features].copy()
    for col in ['US News 排名', '录取率 (%)', '学费 (万 RMB)']: pca_input[col] = 1 - pca_input[col] / pca_input[col].max()
    X_scaled = StandardScaler().fit_transform(pca_input)
    pca = PCA(n_components=2)
    pcs = pca.fit_transform(X_scaled)
    df['PC1'], df['PC2'] = pcs[:, 0], pcs[:, 1]
    
    min_pc1, max_pc1 = df['PC1'].min(), df['PC1'].max()
    user_pc1 = min_pc1 + (effective_ucs / (100 * diff_mult * 1.2)) * (max_pc1 - min_pc1) # 近似映射
    user_pc2 = df['PC2'].mean()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(f"🗺️ {target_country} 留学策略地图 (已校准)")
        fig = px.scatter(df, x='PC1', y='PC2', color='建议类型', hover_name='学校名称', size='SDS_Final',
                         color_discrete_map={"🔴 冲刺校 (Reach)": "#FF6B6B", "🔵 匹配校 (Match)": "#4ECDC4", "🟢 保底校 (Safety)": "#FFE66D"}, opacity=0.6)
        fig.add_scatter(x=[user_pc1], y=[user_pc2], mode='markers+text', marker=dict(symbol='star', size=30, color='black'), text=["<b>您</b>"], showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("📋 完整诊断报告")
        counts = df['建议类型'].value_counts()
        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 冲刺", counts.get("🔴 冲刺校 (Reach)", 0))
        c2.metric("🔵 匹配", counts.get("🔵 匹配校 (Match)", 0))
        c3.metric("🟢 保底", counts.get("🟢 保底校 (Safety)", 0))
        st.divider()
        with st.expander("📂 点击查看完整学校列表 (含修正值)"):
            st.dataframe(df.sort_values('SDS_Final')[['学校名称', 'US News 排名', 'SDS_Raw', 'Correction', 'SDS_Final', '建议类型']], use_container_width=True, hide_index=True)
        
        st.success("**💡 智能提示**：带有 📝 标记的学校表示系统已根据您的历史案例库进行了难度修正。修正值越大，说明真实录取情况与网络预测偏差越大。")

st.divider()
st.info("💡 需要修改信息或录入案例？请点击顶部导航栏。")
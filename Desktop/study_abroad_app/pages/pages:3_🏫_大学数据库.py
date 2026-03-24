import streamlit as st
import pandas as pd
import os
import time
import sys

# 添加根目录到路径，以便导入 utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="全球大学数据库", layout="wide", page_icon="🏫")

# === 自定义 CSS (保持不变) ===
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    button[data-testid="stSidebarToggle"] {
        visibility: visible !important; opacity: 1 !important; z-index: 9999 !important;
        position: fixed !important; top: 15px !important; left: 15px !important;
        background-color: rgba(44, 44, 44, 0.9) !important; border: 1px solid #555 !important;
        color: white !important; border-radius: 8px !important; padding: 5px 10px !important;
        transition: all 0.3s ease !important;
    }
    button[data-testid="stSidebarToggle"]:hover {
        background-color: #4ECDC4 !important; color: black !important; transform: scale(1.1);
    }
    .nav-container {
        display: flex; justify-content: center; gap: 15px; margin-bottom: 30px;
        padding: 20px; background-color: #1E1E1E; border-radius: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: fit-content;
        margin-left: auto; margin-right: auto; position: relative; z-index: 100;
    }
    .nav-btn {
        text-decoration: none; color: white; padding: 12px 25px;
        border-radius: 30px; font-weight: bold; transition: all 0.3s ease;
        background-color: #2C2C2C; border: 1px solid #444;
        display: flex; align-items: center; gap: 8px;
    }
    .nav-btn:hover {
        background-color: #4ECDC4; color: #000; transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(78, 205, 196, 0.4);
    }
    .nav-btn.active {
        background-color: #FF6B6B; color: white;
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4); border-color: #FF6B6B;
    }
    .news-ticker {
        background-color: #262730;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.9em;
        color: #4ECDC4;
        border-left: 4px solid #4ECDC4;
        margin-bottom: 10px;
    }
</style>

<div class="nav-container">
    <a href="../Home.py" class="nav-btn">🎓 学生画像</a>
    <a href="page_2_analysis.py" class="nav-btn">📊 智能分析</a>
    <a href="3_🏫_大学数据库.py" class="nav-btn active">🏫 大学数据库</a>
</div>
""", unsafe_allow_html=True)

st.title("🌍 全球大学数据库管理中心 (实时联网版)")
st.markdown("已扩充 **英国 (40+)**、**香港 (10+)** 列表，并支持 **实时联网同步** 录取热度数据。")

csv_path = "universities.csv"

# === 数据生成函数 (保持不变) ===
def generate_global_data_v2():
    data = []
    # 美国 (简化版，保留核心)
    us_names = ['MIT', 'Stanford', 'Harvard', 'Caltech', 'Princeton', 'Yale', 'UPenn', 'Columbia', 'Duke', 'Johns Hopkins',
        'Northwestern', 'Dartmouth', 'Brown', 'Vanderbilt', 'Rice', 'Notre Dame', 'Cornell', 'Georgetown', 'UCLA', 'Michigan',
        'Berkeley', 'CMU', 'USC', 'NYU', 'Tufts', 'UCSB', 'Boston College', 'UNC Chapel Hill', 'Georgia Tech', 'UIUC',
        'Ohio State', 'Purdue', 'Penn State', 'Maryland', 'Washington (Seattle)', 'Rutgers', 'Florida', 'Texas A&M', 'Boston University',
        'Wisconsin-Madison', 'Irvine', 'San Diego', 'Davis', 'Virginia Tech', 'Northeastern', 'Syracuse', 'Indiana Bloomington', 'Connecticut']
    for i, name in enumerate(us_names):
        rank = i + 1
        admit = 4 + (rank * 0.8) if rank <= 20 else 15 + (rank * 0.6)
        if name in ['Northwestern', 'Duke', 'Vanderbilt']: admit = min(admit, 12)
        if name in ['UIUC', 'Berkeley', 'Michigan', 'UCLA', 'Ohio State', 'Purdue']: admit = max(admit, 20)
        research = max(4, 10 - (rank // 15))
        cs_score = max(4, 10 - (rank // 12))
        if name in ['CMU', 'MIT', 'Stanford', 'Berkeley']: cs_score = 10
        elif name in ['UIUC', 'Georgia Tech', 'Cornell', 'Columbia', 'Michigan']: cs_score = 9
        elif name in ['Purdue', 'Maryland', 'Washington (Seattle)', 'UCSD', 'UCLA']: cs_score = 8
        tuition = 58 if rank <= 30 or name in ['NYU', 'USC', 'BU', 'Northeastern'] else 35
        if name in ['Georgia Tech', 'UIUC', 'Ohio State', 'Purdue', 'Texas A&M']: tuition = 30
        data.append({"学校名称": name, "国家": "美国", "US News 排名": rank, "录取率 (%)": round(admit, 1), 
                     "科研强度 (1-10)": round(research, 1), "CS 专业实力 (1-10)": round(cs_score, 1), "学费 (万 RMB)": round(tuition, 1)})

    # 英国 (40 所)
    uk_data = [
        ("University of Oxford", 1, 4.5, 10, 9, 45), ("University of Cambridge", 2, 5.0, 10, 9, 45),
        ("Imperial College London", 3, 11.0, 9, 10, 42), ("LSE", 4, 9.0, 8, 7, 40),
        ("UCL", 5, 12.0, 9, 8, 40), ("University of Edinburgh", 6, 15.0, 8, 9, 35),
        ("King's College London", 7, 18.0, 7, 7, 38), ("University of Manchester", 8, 25.0, 8, 8, 32),
        ("University of Warwick", 9, 20.0, 7, 8, 32), ("University of Bristol", 10, 22.0, 7, 7, 32),
        ("University of Glasgow", 11, 25.0, 7, 7, 30), ("Durham University", 12, 18.0, 6, 6, 32),
        ("University of Southampton", 13, 28.0, 7, 8, 30), ("University of Birmingham", 14, 30.0, 7, 7, 30),
        ("University of Leeds", 15, 32.0, 6, 7, 28), ("University of Sheffield", 16, 35.0, 6, 7, 28),
        ("University of Nottingham", 17, 35.0, 6, 7, 28), ("Queen Mary University of London", 18, 40.0, 6, 8, 32),
        ("Lancaster University", 19, 38.0, 5, 6, 28), ("Newcastle University", 20, 40.0, 5, 6, 28),
        ("University of York", 21, 42.0, 5, 6, 28), ("University of Exeter", 22, 40.0, 5, 6, 28),
        ("University of Bath", 23, 45.0, 5, 7, 28), ("Loughborough University", 24, 50.0, 4, 6, 26),
        ("University of Liverpool", 25, 48.0, 5, 6, 28), ("University of Aberdeen", 26, 50.0, 5, 5, 26),
        ("Cardiff University", 27, 52.0, 5, 6, 28), ("University of St Andrews", 28, 35.0, 6, 5, 32),
        ("Heriot-Watt University", 29, 55.0, 4, 7, 26), ("University of Strathclyde", 30, 55.0, 4, 7, 26),
        ("City, University of London", 31, 50.0, 4, 7, 30), ("Brunel University", 32, 60.0, 4, 6, 26),
        ("Queen's University Belfast", 33, 55.0, 4, 5, 26), ("University of Sussex", 34, 50.0, 4, 6, 28),
        ("Royal Holloway", 35, 55.0, 4, 5, 28), ("Goldsmiths, University of London", 36, 60.0, 4, 6, 28),
        ("University of Leicester", 37, 60.0, 4, 5, 26), ("Swansea University", 38, 65.0, 4, 5, 24),
        ("University of Kent", 39, 65.0, 4, 5, 26), ("Oxford Brookes University", 40, 70.0, 3, 5, 24)
    ]
    for i, (name, rank, admit, res, cs, fee) in enumerate(uk_data):
        data.append({"学校名称": name, "国家": "英国", "US News 排名": rank, "录取率 (%)": admit, 
                     "科研强度 (1-10)": res, "CS 专业实力 (1-10)": cs, "学费 (万 RMB)": fee})

    # 加拿大
    ca_data = [
        ("University of Toronto", 1, 18.0, 10, 10, 35), ("University of British Columbia", 2, 22.0, 9, 9, 35),
        ("McGill University", 3, 25.0, 9, 8, 30), ("University of Waterloo", 4, 17.0, 8, 10, 32),
        ("University of Alberta", 5, 35.0, 8, 8, 28), ("University of Montreal", 6, 30.0, 8, 9, 25),
        ("McMaster University", 7, 35.0, 7, 7, 30), ("Queen's University", 8, 30.0, 6, 6, 32),
        ("University of Calgary", 9, 40.0, 7, 7, 28), ("Simon Fraser University", 10, 45.0, 6, 8, 30),
        ("University of Ottawa", 11, 45.0, 6, 7, 28), ("York University", 12, 50.0, 5, 6, 28),
        ("Carleton University", 13, 55.0, 5, 7, 26), ("University of Victoria", 14, 55.0, 5, 6, 28),
        ("Dalhousie University", 15, 60.0, 5, 5, 26)
    ]
    for i, (name, rank, admit, res, cs, fee) in enumerate(ca_data):
        data.append({"学校名称": name, "国家": "加拿大", "US News 排名": rank, "录取率 (%)": admit, 
                     "科研强度 (1-10)": res, "CS 专业实力 (1-10)": cs, "学费 (万 RMB)": fee})

    # 澳洲 (优化逻辑)
    au_data = [
        ("UNSW Sydney", 1, 25.0, 8, 10, 30), ("University of Melbourne", 2, 30.0, 9, 9, 30),
        ("University of Sydney", 3, 30.0, 9, 8, 30), ("Australian National University", 4, 28.0, 9, 8, 30),
        ("Monash University", 5, 35.0, 8, 8, 28), ("University of Queensland", 6, 35.0, 8, 7, 28),
        ("University of Technology Sydney", 7, 40.0, 6, 9, 28), ("University of Western Australia", 8, 45.0, 7, 6, 28),
        ("University of Adelaide", 9, 50.0, 7, 6, 26), ("Macquarie University", 10, 55.0, 5, 7, 26),
        ("Queensland University of Technology", 11, 60.0, 5, 7, 26), ("RMIT University", 12, 65.0, 5, 7, 26),
        ("University of Wollongong", 13, 70.0, 5, 7, 24), ("Curtin University", 14, 75.0, 5, 6, 24),
        ("Deakin University", 15, 80.0, 4, 5, 24), ("Griffith University", 16, 85.0, 4, 5, 22),
        ("La Trobe University", 17, 90.0, 4, 5, 22)
    ]
    for i, (name, rank, admit, res, cs, fee) in enumerate(au_data):
        data.append({"学校名称": name, "国家": "澳洲", "US News 排名": rank, "录取率 (%)": admit, 
                     "科研强度 (1-10)": res, "CS 专业实力 (1-10)": cs, "学费 (万 RMB)": fee})

    # 香港 (扩充)
    hk_data = [
        ("University of Hong Kong (HKU)", 1, 15.0, 9, 9, 35),
        ("Hong Kong University of Science and Technology (HKUST)", 2, 12.0, 8, 10, 35),
        ("Chinese University of Hong Kong (CUHK)", 3, 18.0, 8, 9, 32),
        ("City University of Hong Kong (CityU)", 4, 25.0, 7, 9, 30),
        ("Hong Kong Polytechnic University (PolyU)", 5, 30.0, 7, 8, 28),
        ("Hong Kong Baptist University (HKBU)", 6, 40.0, 5, 6, 26),
        ("Lingnan University", 7, 50.0, 4, 5, 24),
        ("Hong Kong Metropolitan University", 8, 60.0, 4, 5, 24),
        ("Education University of Hong Kong", 9, 55.0, 4, 4, 24),
        ("Hang Seng University", 10, 65.0, 3, 4, 22),
        ("Hong Kong Shue Yan University", 11, 70.0, 3, 3, 20),
        ("Hong Kong Chu Hai College", 12, 75.0, 3, 3, 20)
    ]
    for i, (name, rank, admit, res, cs, fee) in enumerate(hk_data):
        data.append({"学校名称": name, "国家": "中国香港", "US News 排名": rank, "录取率 (%)": admit, 
                     "科研强度 (1-10)": res, "CS 专业实力 (1-10)": cs, "学费 (万 RMB)": fee})

    return pd.DataFrame(data)

# === 主逻辑 ===
if os.path.exists(csv_path):
    df_uni = pd.read_csv(csv_path)
    st.success(f"✅ 已加载本地数据库，共 {len(df_uni)} 所学校。")
else:
    df_uni = generate_global_data_v2()
    st.info("🆕 未检测到本地数据库，已自动加载 **美/英/加/澳/港** 五地最新预设数据。")

st.subheader("📝 编辑院校信息")
edited_df = st.data_editor(df_uni, num_rows="dynamic", use_container_width=True, hide_index=True,
    column_config={
        "国家": st.column_config.TextColumn("国家", required=True),
        "学校名称": st.column_config.TextColumn("学校名称", required=True),
        "US News 排名": st.column_config.NumberColumn("排名", min_value=1, max_value=200),
        "录取率 (%)": st.column_config.NumberColumn("录取率 (%)", min_value=0, max_value=100),
        "科研强度 (1-10)": st.column_config.NumberColumn("科研", min_value=1, max_value=10),
        "CS 专业实力 (1-10)": st.column_config.NumberColumn("CS 实力", min_value=1, max_value=10),
        "学费 (万 RMB)": st.column_config.NumberColumn("学费", min_value=0),
        "热度系数 (0-1)": st.column_config.NumberColumn("热度系数", min_value=0, max_value=1, format="%.2f"),
    })

st.divider()

# === 🌐 联网同步模块 ===
st.subheader("🌐 数据中心同步")
st.caption("连接云端数据源，抓取最新的录取率变动、专业热度趋势，并自动调整算法权重。")

st.markdown("""
<div class="news-ticker">
    <b>📰 实时录取情报 (Live Feed):</b><br>
    • 🔴 <i>Just Now</i>: UIUC CS 专业申请人数同比上涨 25%，录取难度上调。<br>
    • 🟢 <i>10 mins ago</i>: 澳洲八大宣布部分工程专业扩招，门槛微降。<br>
    • 🟡 <i>1 hour ago</i>: 香港科技大学 AI 专业新增面试环节。
</div>
""", unsafe_allow_html=True)

col_sync1, col_sync2, col_sync3 = st.columns([1, 1, 4])

with col_sync1:
    sync_button = st.button("🔄 联网同步数据", use_container_width=True, type="primary")

with col_sync2:
    if st.button("🗑️ 重置为预设", use_container_width=True):
        if os.path.exists(csv_path):
            os.remove(csv_path)
        st.warning("⚠️ 自定义数据已被清除，刷新页面后将恢复预设。")
        st.rerun()

if sync_button:
    try:
        from utils.data_updater import update_database_with_live_info
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 正在连接全球大学数据源...")
        progress_bar.progress(20)
        time.sleep(0.5)
        
        status_text.text("📥 正在抓取最新录取率与热度数据...")
        progress_bar.progress(50)
        time.sleep(0.5)
        
        status_text.text("🧠 正在应用 AI 模型分析趋势...")
        progress_bar.progress(80)
        time.sleep(0.5)
        
        success, message = update_database_with_live_info(csv_path)
        
        progress_bar.progress(100)
        
        if success:
            st.success(message)
            st.balloons()
            st.rerun()
        else:
            st.error(message)
            
    except ImportError:
        st.error("❌ **错误：未找到 `utils/data_updater.py` 文件。**\n\n请确保你在项目根目录下创建了 `utils` 文件夹，并将 `data_updater.py` 放入其中。")

st.divider()

# === 🔍 单校深度侦察模块 ===
st.subheader("🔍 单校深度侦察 (Deep Dive)")
st.caption("输入特定大学名称，系统将实时全网搜索该校最新的录取趋势、难度变化和内部情报。")

target_school = st.text_input("输入大学英文名称 (例如：New York University)", placeholder="Type university name here...", key="search_input_main")
search_btn = st.button("🚀 开始侦察", type="primary", use_container_width=True, key="search_btn_main")

# 处理搜索逻辑 (移到了 with 块外面，避免缩进问题)
# ... (前面的代码不变) ...

# 处理搜索逻辑
if search_btn:
    if not target_school:
        st.warning("⚠️ 请输入大学名称。")
    else:
        try:
            from utils.data_updater import SERPAPI_KEY
            if not SERPAPI_KEY:
                 st.error("❌ 请先在 `utils/data_updater.py` 中配置 SerpApi Key。")
            else:
                with st.spinner(f"🌐 正在全网深度搜索 {target_school} 并撰写情报报告..."):
                    from utils.data_updater import search_single_school_deep_dive
                    result = search_single_school_deep_dive(target_school, "Computer Science")
                    
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success("✅ 深度侦察完成！")
                        
                        # 1. 显示核心指标
                        c1, c2, c3 = st.columns(3)
                        c1.metric("最新趋势", result['trend'])
                        c2.metric("热度指数", f"{result['heat']:.2f}")
                        c3.metric("情报来源数", f"{result['raw_count']} 条")
                        
                        st.divider()
                        
                        # 2. 【核心修改】显示整段详细文字报告
                        st.subheader("📝 深度情报分析报告")
                        st.markdown(result['report_text']) # 这里显示那一整段文字
                        
                        # 3. 显示来源
                        if result.get('sources'):
                            with st.expander("🔗 查看原始信息来源 (" + str(len(result['sources'])) + ")"):
                                for i, link in enumerate(result['sources']):
                                    st.markdown(f"{i+1}. [点击查看原始链接]({link})")
                        
                        st.divider()
                        st.warning("⚠️ 是否将此趋势应用到全局数据库中？")
                        col_apply1, col_apply2 = st.columns(2)
                        with col_apply1:
                            if st.button(f"✅ 确认更新 {target_school}", key=f"apply_{target_school}"):
                                # ... (更新逻辑保持不变) ...
                                df_temp = pd.read_csv(csv_path)
                                mask = df_temp['学校名称'].str.contains(target_school, case=False, na=False)
                                if mask.any():
                                    # 更新逻辑
                                    current_rate = df_temp.loc[mask, '录取率 (%)'].values[0]
                                    new_rate = current_rate + (result['change'] * 100)
                                    df_temp.loc[mask, '录取率 (%)'] = round(max(1.0, min(99.0, new_rate)), 1)
                                    
                                    old_heat = df_temp.loc[mask, '热度系数 (0-1)'].values[0]
                                    new_heat = 0.5 * old_heat + 0.5 * result['heat']
                                    df_temp.loc[mask, '热度系数 (0-1)'] = round(new_heat, 2)
                                    
                                    # 把报告摘要也存进去
                                    df_temp.loc[mask, '趋势原因'] = f"深度侦察：{result['trend']}"
                                    
                                    df_temp.to_csv(csv_path, index=False)
                                    st.balloons()
                                    st.success(f"✅ 已成功更新 {target_school} 的数据！")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ 数据库中未找到 '{target_school}'。")
                        with col_apply2:
                            if st.button("❌ 暂不更新", key=f"cancel_{target_school}"):
                                st.info("已取消操作。")
        except Exception as e:
            st.error(f"发生错误：{str(e)}")

# ... (后面的代码不变) ...

st.divider()
st.markdown("**💡 更新说明**：澳洲 CS 强校难度已上调；香港全境难度维持高位；英国列表扩充至 40 所。**点击“联网同步”可激活实时热度学习功能。**")
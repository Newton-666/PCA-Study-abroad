import streamlit as st
import time
import pandas as pd
import os

# 页面配置
st.set_page_config(page_title="Step 1: 学生画像构建", layout="wide", page_icon="🎓")

# === 自定义 CSS (包含侧边栏按钮修复 + 导航栏) ===
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
</style>
<div class="nav-container">
    <a href="Home.py" class="nav-btn active">🎓 学生画像</a>
    <a href="pages/page_2_analysis.py" class="nav-btn">📊 智能分析</a>
    <a href="pages/3_🏫_大学数据库.py" class="nav-btn">🏫 大学数据库</a>
</div>
""", unsafe_allow_html=True)

st.title("🎓 第一步：构建核心竞争力的画像")
st.divider()

# === 初始化 Session State ===
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'al_subjects' not in st.session_state:
    st.session_state.al_subjects = [{"id": 0, "grade": "A"}]

# === 核心数据库：专业 - 竞赛映射表 ===
MAJOR_COMPETITIONS = {
    "cs": [
        ("USACO (计算机奥林匹克)", ["Platinum (白金)", "Gold (金)", "Silver (银)", "Bronze (铜)", "Participated"]),
        ("AMC 10/12 (数学竞赛)", ["AIME Qualifier + DHR", "AIME Qualifier + HR", "AIME Qualifier", "Distinction (前 5%)", "Participated"]),
        ("IOI / NOI (信息学奥赛)", ["Gold Medal", "Silver Medal", "Bronze Medal", "Participated"]),
        ("Kaggle (数据科学)", ["Grandmaster", "Master", "Expert", "Contributor", "Novice"]),
        ("Hackathon (黑客马拉松)", ["Winner / Best Project", "Finalist", "Participant"]),
        ("Research Paper (科研论文)", ["Top Conference (CCF-A)", "Workshop / Journal", "ArXiv Preprint"])
    ],
    "business": [
        ("FBLA (未来商业领袖)", ["National 1st Place", "National Top 10", "State Level", "Participated"]),
        ("NEC (经济学挑战)", ["Global Gold / Critical Distinction", "Global Silver / Distinction", "Regional Level", "Participated"]),
        ("DECA (商业模拟)", ["International Finalist", "State/Province Level", "District Level", "Participated"]),
        ("Wharton Global Investment", ["Top 100 Teams", "Regional Semifinalist", "Participated"]),
        ("Marshall Business Case", ["Winner", "Finalist", "Participant"])
    ],
    "stem": [
        ("Physics Bowl (物理碗)", ["Global Top 100", "Gold Medal", "Silver Medal", "Participated"]),
        ("Chemistry Olympiad (化学奥赛)", ["National Medal", "Regional Medal", "Participated"]),
        ("Biology Olympiad (生物奥赛)", ["National Medal", "Regional Medal", "Participated"]),
        ("ISEF / STS (科学与工程)", ["Finalist / Award Winner", "Qualifier", "Participant"]),
        ("Robotics (FRC/VEX)", ["World Championship Qualifier", "Regional Winner", "Participant"])
    ],
    "humanities": [
        ("John Locke Essay Competition", ["Global Winner / High Commendation", "Shortlisted", "Submitted"]),
        ("NYT Student Review", ["Published", "Honorable Mention", "Submitted"]),
        ("Scholastic Art & Writing", ["National Gold Medal", "National Silver Medal", "Regional Award", "Participated"]),
        ("Model UN (模联)", ["Best Delegate", "Honorable Mention", "Participant"])
    ]
}

def get_competitions_for_major(major_name):
    major_lower = major_name.lower()
    matched_comps = []
    if any(k in major_lower for k in ["computer", "cs", "software", "data", "ai", "machine"]):
        matched_comps.extend(MAJOR_COMPETITIONS["cs"])
    if any(k in major_lower for k in ["business", "finance", "econ", "management", "marketing"]):
        matched_comps.extend(MAJOR_COMPETITIONS["business"])
    if any(k in major_lower for k in ["physics", "chemistry", "biology", "math", "engineering", "robotics"]):
        matched_comps.extend(MAJOR_COMPETITIONS["stem"])
    if any(k in major_lower for k in ["history", "philosophy", "literature", "psychology", "sociology", "art"]):
        matched_comps.extend(MAJOR_COMPETITIONS["humanities"])
    
    if not matched_comps:
        return [("General Research", ["Published", "Presented", "In Progress"]), 
                ("Community Service", ["100+ Hours", "50+ Hours", "Leader", "Volunteer"]),
                ("Sports / Arts", ["National Level", "Regional Level", "School Team", "Hobbyist"])]
    return matched_comps

# === 第一部分：学术背景设置 ===
st.subheader("1️⃣ 学术背景设置")
col_sel1, col_sel2 = st.columns(2)

with col_sel1:
    country = st.selectbox("目标留学国家/地区", ["美国", "英国", "加拿大", "澳洲", "中国香港"], key="country_selector")
    curriculum = st.selectbox("高中课程体系", ["IB", "A-Level", "AP", "普高"], key="curriculum_selector")

with col_sel2:
    target_major = st.text_input("目标专业", "Computer Science", key="major_input")
    if 'last_major' not in st.session_state or st.session_state.last_major != target_major:
        st.session_state.last_major = target_major
        comps = get_competitions_for_major(target_major)
        st.session_state.us_activities = [
            {"id": i, "name": name, "award": awards[0]} 
            for i, (name, awards) in enumerate(comps[:3])
        ]

st.divider()

# === 动态输入区域：学术成绩 ===
gpa_4_0 = 0.0
gpa_raw_display = ""

if curriculum == "IB":
    st.markdown("**📘 IB 成绩录入**")
    c1, c2, c3 = st.columns(3)
    subjects = ["HL 1", "HL 2", "HL 3", "SL 1", "SL 2", "SL 3"]
    total_points = 0
    for i, sub in enumerate(subjects):
        col = [c1, c2, c3][i % 3]
        with col:
            pts = st.number_input(f"{sub} (1-7)", min_value=1, max_value=7, value=7, key=f"ib_pts_{i}")
            total_points += pts
    core_points = st.number_input("核心分 (EE + TOK, 0-3)", min_value=0, max_value=3, value=3, key="ib_core")
    final_ib_score = total_points + core_points
    gpa_raw_display = f"IB Total: {final_ib_score}/45"
    gpa_4_0 = min(4.0, max(1.0, 1.0 + (final_ib_score - 24) / 18 * 3.0))
elif curriculum == "A-Level":
    st.markdown("**🇬 A-Level 成绩录入**")
    total_ucas = 0
    grade_map = {'A*': 56, 'A': 48, 'B': 40, 'C': 32, 'D': 24, 'E': 16}
    for i, subj in enumerate(st.session_state.al_subjects):
        c_a, c_b, c_c = st.columns([4, 2, 1])
        with c_a: st.text_input(f"科目 {i+1}", value=f"Subject {i+1}", key=f"al_name_{subj['id']}")
        with c_b:
            grade = st.selectbox("等级", ['A*', 'A', 'B', 'C', 'D', 'E'], index=1, key=f"al_grade_{subj['id']}")
            total_ucas += grade_map[grade]
        with c_c:
            if st.button("🗑️", key=f"del_{subj['id']}"):
                st.session_state.al_subjects.pop(i)
                st.rerun()
    if len(st.session_state.al_subjects) < 5 and st.button("+ 添加一门课", key="add_al_subj"):
        new_id = max([s['id'] for s in st.session_state.al_subjects]) + 1 if st.session_state.al_subjects else 1
        st.session_state.al_subjects.append({"id": new_id, "grade": "A"})
        st.rerun()
    gpa_raw_display = f"UCAS Points: {total_ucas}"
    gpa_4_0 = min(4.0, (total_ucas / 168.0) * 4.0 * 1.1)
else:
    st.markdown("**🇺 AP / 普高体系**")
    gpa_input = st.number_input("GPA / 平均分", min_value=0.0, max_value=100.0, value=90.0, step=0.1, key="gen_gpa")
    gpa_4_0 = gpa_input / 25.0 if gpa_input > 4.0 else gpa_input
    gpa_raw_display = f"Score: {gpa_input}"

st.divider()

# === 语言考试 ===
st.subheader("2️⃣ 语言与标准化考试")
col_l1, col_l2 = st.columns(2)
with col_l1:
    toefl = st.number_input("托福 (TOEFL)", min_value=0, max_value=120, value=100, step=1, key="toefl_input")
with col_l2:
    ielts = st.number_input("雅思 (IELTS)", min_value=0.0, max_value=9.0, value=7.0, step=0.5, key="ielts_input")
lang_score_final = max(toefl, ielts * 13.5)
lang_display = f"TOEFL: {toefl}" if toefl >= ielts * 13.5 else f"IELTS: {ielts}"

# === 美国特有项 & 动态竞赛列表 ===
sat_score = 0
if country == "美国":
    st.divider()
    st.subheader("🇺 美国申请特有项")
    sat_score = st.number_input("SAT (可选)", min_value=0, max_value=1600, value=1500, step=10, key="sat_input")
    if sat_score > 0: st.caption(f"💡 SAT {sat_score}")
    else: st.caption("💡 Test-Optional")
    
    st.divider()
    st.subheader(f"🏆 {target_major} 核心竞赛与活动")
    st.caption("系统已根据您的专业自动预填相关竞赛，请如实选择获奖等级。")
    
    current_comps = get_competitions_for_major(target_major)
    comp_dict = {name: awards for name, awards in current_comps}
    
    for i, act in enumerate(st.session_state.us_activities):
        c_act1, c_act2, c_act3 = st.columns([4, 3, 1])
        with c_act1:
            available_names = list(comp_dict.keys())
            act_name = st.selectbox("竞赛/活动名称", available_names, index=available_names.index(act['name']) if act['name'] in available_names else 0, key=f"us_act_name_{act['id']}")
        with c_act2:
            awards_list = comp_dict.get(act_name, ["Participated"])
            current_award = act['award'] if act['award'] in awards_list else awards_list[0]
            act_award = st.selectbox("获奖等级", awards_list, index=awards_list.index(current_award), key=f"us_act_award_{act['id']}")
        with c_act3:
            if st.button("🗑️", key=f"del_us_{act['id']}"):
                st.session_state.us_activities.pop(i)
                st.rerun()
        
        st.session_state.us_activities[i]['name'] = st.session_state[f"us_act_name_{act['id']}"]
        st.session_state.us_activities[i]['award'] = st.session_state[f"us_act_award_{act['id']}"]

    if len(st.session_state.us_activities) < 6 and st.button("+ 添加一项活动", key="add_us_act"):
        new_id = max([a['id'] for a in st.session_state.us_activities]) + 1 if st.session_state.us_activities else 1
        default_comp_name = list(comp_dict.keys())[0]
        st.session_state.us_activities.append({"id": new_id, "name": default_comp_name, "award": comp_dict[default_comp_name][0]})
        st.rerun()
else:
    st.info(f"🌏 申请 {country} 重点关注学术成绩。")

st.divider()

# === 表单提交区 ===
with st.form("profile_wizard"):
    st.subheader("3️⃣ 综合软实力评估")
    research_level = st.selectbox("整体科研深度", ["无", "校内课题", "省级/州级获奖", "国家级获奖/论文", "顶会/国际大奖"], key="research_sel")
    activity_level = st.selectbox("整体活动影响力", ["普通参与者", "社团骨干", "创始人/主席", "区域性知名", "国家级/国际级"], key="activity_sel")
    st.divider()
    st.subheader("4️⃣ 其他约束")
    budget = st.slider("年度预算 (万人民币)", 10, 100, 50, 5, key="budget_slider")
    
    submitted = st.form_submit_button("🚀 生成能力模型并进入分析", use_container_width=True, type="primary")

if submitted:
    # === 1. 基础映射 ===
    research_map = {"无": 10, "校内课题": 30, "省级/州级获奖": 60, "国家级获奖/论文": 85, "顶会/国际大奖": 100}
    activity_map = {"普通参与者": 10, "社团骨干": 40, "创始人/主席": 70, "区域性知名": 90, "国家级/国际级": 100}
    
    base_r_score = research_map[research_level]
    base_a_score = activity_map[activity_level]
    
    # === 2. 竞赛加分 ===
    final_a_score = base_a_score
    if country == "美国" and len(st.session_state.us_activities) > 0:
        all_awards_map = {}
        for comp, awards in current_comps:
            step = 90 / (len(awards) - 1) if len(awards) > 1 else 0
            for idx, aw in enumerate(awards):
                score = 100 - (idx * step)
                all_awards_map[aw] = score
        
        max_award_score = 0
        for act in st.session_state.us_activities:
            award_val = all_awards_map.get(act['award'], 10)
            if award_val > max_award_score: max_award_score = award_val
        final_a_score = (base_a_score * 0.4) + (max_award_score * 0.6)
    
    r_score = base_r_score
    a_score = min(100, final_a_score)
    
    # === 3. 【核心修复】硬指标重算 ===
    gpa_final = gpa_4_0 * 25
    lang_score = lang_score_final
    
    sat_bonus_raw = 0
    if country == "美国" and sat_score > 0:
        sat_bonus_raw = (sat_score - 1000) / 600 * 25
        sat_bonus_raw = max(0, min(25, sat_bonus_raw))
    
    base_hard = (gpa_final * 0.4) + (lang_score * 0.3) + (sat_bonus_raw * 0.3)
    
    elite_bonus = 0
    if gpa_final >= 95 and lang_score >= 105:
        elite_bonus = 10
    
    hard_score = min(100, base_hard + elite_bonus)
    
    # === 4. 【核心修复】UCS 总分校准 ===
    raw_uc = (r_score * 0.20) + (a_score * 0.20) + (hard_score * 0.50) + ((budget/100)*10 * 0.1)
    
    # === 5. 动态惩罚 ===
    penalty = 0
    user_tier = "Normal"
    is_top_tier = (a_score > 75) or (hard_score > 85)
    
    if is_top_tier and toefl < 110:
        user_tier = "Top Tier (High Risk)"
        deficit = 110 - toefl
        penalty = deficit * 0.8 
        st.toast(f"🚨 检测到顶尖背景但托福 ({toefl}) 低于 110！触发木桶效应惩罚：-{penalty:.1f} 分", icon="🚨")
    elif not is_top_tier and toefl < 100:
        user_tier = "Normal (Low Impact)"
        deficit = 100 - toefl
        penalty = deficit * 0.2
    
    penalty = max(0, penalty)
    ucs = raw_uc - penalty
    ucs = max(0, min(100, ucs))
    
    st.session_state.user_data = {
        "country": country, "curriculum": curriculum, "gpa_raw": gpa_raw_display, "gpa_4_0": gpa_4_0,
        "toefl": toefl, "ielts": ielts, "lang_best": lang_display,
        "sat": sat_score if country == "美国" else None,
        "research": research_level, "research_score": r_score,
        "activity": activity_level, "activity_score": a_score,
        "us_activities": st.session_state.us_activities if country == "美国" else [],
        "budget": budget, "major": target_major, 
        "ucs": ucs, 
        "hard_score": hard_score,
        "penalty": penalty,
        "user_tier": user_tier
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    steps = [f"解析 {curriculum}...", f"评估 {country}...", "量化竞赛权重...", "应用动态惩罚...", "计算 UCS...", "跳转..."]
    for i, step in enumerate(steps):
        status_text.text(step)
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(0.3)
    status_text.text("✅ 准备就绪！")
    time.sleep(0.5)
    st.switch_page("pages/page_2_analysis.py")
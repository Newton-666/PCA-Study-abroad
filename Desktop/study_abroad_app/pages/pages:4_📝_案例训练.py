import streamlit as st
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === 直接在当前文件定义别名逻辑，避免导入错误 ===
SCHOOL_ALIASES = {
    "港理工": ["Hong Kong Polytechnic University", "PolyU"],
    "科大": ["Hong Kong University of Science and Technology", "HKUST"],
    "港大": ["University of Hong Kong", "HKU"],
    "中文大学": ["Chinese University of Hong Kong", "CUHK"],
    "城大": ["City University of Hong Kong", "CityU"],
    "浸会": ["Hong Kong Baptist University", "HKBU"],
    "多大": ["University of Toronto", "UofT"],
    "ubc": ["University of British Columbia"],
    "麦吉尔": ["McGill University"],
    "滑铁卢": ["University of Waterloo"],
    "mit": ["Massachusetts Institute of Technology"],
    "斯坦福": ["Stanford University"],
    "哈佛": ["Harvard University"],
    "剑桥": ["University of Cambridge"],
    "牛津": ["University of Oxford"],
    "帝国理工": ["Imperial College London", "IC"],
    "ucl": ["University College London"],
    "爱丁堡": ["University of Edinburgh"],
    "曼大": ["University of Manchester"],
    "华威": ["University of Warwick"],
    "新南威尔士": ["UNSW Sydney", "UNSW"],
    "墨尔本": ["University of Melbourne"],
    "悉尼大学": ["University of Sydney"],
    "澳国立": ["Australian National University", "ANU"],
    "cmu": ["Carnegie Mellon University"],
    "nyu": ["New York University"],
    "usc": ["University of Southern California"],
    "ucb": ["University of California, Berkeley"],
    "ucla": ["University of California, Los Angeles"],
    "ucsd": ["University of California, San Diego"],
    "uiuc": ["University of Illinois at Urbana-Champaign"],
    "gatech": ["Georgia Institute of Technology"],
    "西北": ["Northwestern University"],
    "杜克": ["Duke University"],
    "哥大": ["Columbia University"],
    "宾大": ["University of Pennsylvania", "UPenn"],
    "康奈尔": ["Cornell University"],
    "布朗": ["Brown University"],
    "达特茅斯": ["Dartmouth College"],
    "普林斯顿": ["Princeton University"],
    "耶鲁": ["Yale University"]
}

def normalize_school_name(name):
    if not name: return ""
    name_lower = name.lower().strip()
    for alias, standards in SCHOOL_ALIASES.items():
        if name_lower == alias.lower() or name_lower in [s.lower() for s in standards]:
            return standards[0]
        for s in standards:
            if s.lower() in name_lower: return s
    return name

# 导入其他函数
from utils.case_trainer import load_cases, save_case, get_school_stats

st.set_page_config(page_title="案例训练中心", layout="wide", page_icon="📝")

# === CSS & 导航栏 ===
st.markdown("""
<style>
    .nav-container { display: flex; justify-content: center; gap: 15px; margin-bottom: 30px; padding: 20px; background-color: #1E1E1E; border-radius: 50px; width: fit-content; margin-left: auto; margin-right: auto; }
    .nav-btn { text-decoration: none; color: white; padding: 12px 25px; border-radius: 30px; font-weight: bold; background-color: #2C2C2C; border: 1px solid #444; transition: all 0.3s; }
    .nav-btn:hover { background-color: #FF9F43; color: #000; transform: translateY(-2px); }
    .nav-btn.active { background-color: #FF9F43; color: #000; border-color: #FF9F43; box-shadow: 0 0 15px rgba(255, 159, 67, 0.4); }
    .stForm { border: 1px solid #333; padding: 25px; border-radius: 15px; background-color: #161616; }
</style>
<div class="nav-container">
    <a href="../Home.py" class="nav-btn">🎓 学生画像</a>
    <a href="page_2_analysis.py" class="nav-btn">📊 智能分析</a>
    <a href="3_🏫_大学数据库.py" class="nav-btn">🏫 大学数据库</a>
    <a href="4_📝_案例训练.py" class="nav-btn active">📝 案例训练</a>
</div>
""", unsafe_allow_html=True)

st.title("📝 真实案例训练中心 (RLHF)")
st.markdown("通过录入真实的录取/拒绝案例，系统将自动校准对各大学的难度预测。**支持中文别名搜索**（如输入“港理工”可自动匹配 PolyU）。")
st.divider()

col_input, col_monitor = st.columns([7, 3])

with col_input:
    st.subheader("➕ 录入新案例")
    
    with st.form("case_form", clear_on_submit=True):
        # 1. 基础信息 (新增国家和轮次)
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            school = st.text_input("学校名称 (英文)", placeholder="e.g. Hong Kong Polytechnic University")
        with c2:
            major = st.text_input("专业", value="Computer Science")
        with c3:
            country = st.selectbox("申请国家/地区", ["美国", "英国", "加拿大", "澳洲", "中国香港", "其他"], index=4)
            
        # 动态申请轮次选项
        round_options = ["Regular Decision (RD)"]
        if country == "美国":
            round_options = ["Early Decision (ED)", "Early Action (EA)", "Regular Decision (RD)", "Rolling"]
        elif country == "英国":
            round_options = ["Oxbridge / Early (Oct 15)", "Standard Early (Jan)", "Clearing"]
        elif country == "加拿大":
            round_options = ["Early (Nov-Jan)", "Regular (Feb-Mar)", "Rolling"]
            
        round_type = st.selectbox("申请轮次", round_options)
        
        st.divider()
        
        # 2. 课程体系选择 (保持原有逻辑)
        st.markdown("### 🎓 成绩详情")
        curriculum = st.selectbox(
            "选择该学生的课程体系",
            ["IB (International Baccalaureate)", "A-Level", "AP / US High School", "中国本科 / 普高 (CGPA/Percentage)"],
            key="curriculum_selector"
        )
        
        grades_dict = {}
        
        if curriculum == "IB (International Baccalaureate)":
            st.info("📘 IB 体系：请输入总分及 6 门具体科目成绩")
            grades_dict["IB Total"] = st.text_input("总分 (0-45)", value="40", key="ib_total")
            grades_dict["Core (EE/TOK)"] = st.text_input("核心分 (0-3)", value="2", key="ib_core")
            st.markdown("**📚 6 门科目成绩**")
            c_sub1, c_sub2, c_sub3 = st.columns(3)
            defaults = ["Math AA/AI HL", "Physics HL", "Chemistry HL", "English SL", "History SL", "Chinese SL"]
            for i in range(6):
                col = [c_sub1, c_sub2, c_sub3][i % 3]
                with col:
                    sub_name = st.text_input(f"科目 {i+1} 名称", value=defaults[i], key=f"ib_sub_name_{i}")
                    sub_grade = st.text_input(f"科目 {i+1} 等级 (1-7)", value="6", key=f"ib_sub_grade_{i}")
                    if sub_name and sub_grade: grades_dict[sub_name] = sub_grade

        elif curriculum == "A-Level":
            st.info("🇬 A-Level 体系：请输入具体科目及等级")
            c_al1, c_al2, c_al3, c_al4 = st.columns(4)
            defaults = ["Math", "Further Math", "Physics", "Chemistry"]
            for i in range(4):
                col = [c_al1, c_al2, c_al3, c_al4][i]
                with col:
                    sub_name = st.text_input(f"科目 {i+1}", value=defaults[i], key=f"al_sub_name_{i}")
                    sub_grade = st.text_input(f"等级 (A*-E)", value="A*", key=f"al_sub_grade_{i}")
                    if sub_name and sub_grade: grades_dict[sub_name] = sub_grade
                
        elif curriculum == "AP / US High School":
            st.info("🇺 AP / 美高体系")
            c_ap1, c_ap2, c_ap3 = st.columns(3)
            with c_ap1:
                grades_dict["GPA"] = st.text_input("GPA (0-4.0)", value="3.8", key="ap_gpa")
                grades_dict["Weighted GPA"] = st.text_input("加权 GPA (可选)", value="4.2", key="ap_wgpa")
            with c_ap2:
                grades_dict["AP Count"] = st.text_input("AP 门数", value="5", key="ap_count")
                grades_dict["AP Avg Score"] = st.text_input("AP 平均分", value="4.5", key="ap_avg")
            with c_ap3:
                grades_dict["SAT"] = st.text_input("SAT (可选)", value="1500", key="ap_sat")
                
        elif curriculum == "中国本科 / 普高 (CGPA/Percentage)":
            st.info("🇨 中国体系")
            c_cn1, c_cn2, c_cn3 = st.columns(3)
            with c_cn1:
                grades_dict["Weighted Avg"] = st.text_input("加权均分 (0-100)", value="88", key="cn_avg")
                grades_dict["Major Avg"] = st.text_input("专业课均分", value="90", key="cn_major")
            with c_cn2:
                grades_dict["Ranking"] = st.text_input("排名 (如 5/100 或 Top 5%)", value="10%", key="cn_rank")
                grades_dict["School Tier"] = st.text_input("学校层次 (985/211/双非)", value="211", key="cn_tier")
            with c_cn3:
                grades_dict["IELTS/TOEFL"] = st.text_input("语言成绩", value="7.0", key="cn_lang")

        st.divider()
        
        # 3. 核心评分与结果
        c_ucs, c_res = st.columns([1, 2])
        with c_ucs:
            ucs = st.number_input("背景综合评分 (UCS)", min_value=0, max_value=100, step=1, help="去'智能分析'页查看该学生的 UCS 分数")
        with c_res:
            result = st.selectbox("申请结果", ["Accepted", "Rejected", "Waitlisted"])
            
        notes = st.text_area("备注 (可选)", placeholder="例如：面试表现好，有特殊奖项，或 ED 早申等", height=80)
        
        submitted = st.form_submit_button("💾 提交案例并训练模型", type="primary", use_container_width=True)
        
        if submitted:
            if school:
                # ✅ 修复点：确保这里有 8 个参数，顺序正确
                save_case(school, country, major, grades_dict, ucs, round_type, result, notes)
                st.success(f"✅ 案例已保存！系统已记录 `{school}` ({country}-{round_type}) 的详细成绩。")
                st.balloons()
                st.rerun()
            else:
                st.error("请输入学校名称。")

with col_monitor:
    st.subheader("🎯 实时修正监控")
    st.caption("支持中文别名搜索，如输入 '港理工' 可查 PolyU。")
    
    if 'query_school' not in st.session_state:
        st.session_state.query_school = ""
        
    school_query = st.text_input("输入学校名查询 (中/英)", value=st.session_state.query_school, key="monitor_input")
    
    if school_query:
        standard_name = normalize_school_name(school_query)
        if standard_name != school_query:
            st.info(f"🔍 已自动识别为：**{standard_name}**")
            
        stats = get_school_stats(school_query)
        if stats:
            st.metric("收录案例总数", stats['total'])
            c_acc, c_rej = st.columns(2)
            c_acc.metric("✅ 录取", stats['accepted_count'])
            c_rej.metric("❌ 拒绝", stats['rejected_count'])
            
            if stats['avg_ucs_accepted'] > 0:
                st.divider()
                st.success(f"**成功案例平均 UCS**: {stats['avg_ucs_accepted']:.1f}")
                st.info(f"**模型行为**: 难度将向 **{stats['avg_ucs_accepted']:.1f}** 分靠拢。")
                st.caption(f"最近录取：{stats['recent_grades']}")
            else:
                st.warning("暂无成功案例。")
        else:
            st.info(f"🔍 未找到 '{standard_name}' 的案例。")
    else:
        st.write("👈 请在上方输入学校名称查看监控数据。")

st.divider()
st.subheader("📊 历史案例库")
df = load_cases()
if not df.empty:
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        filter_school = st.text_input("🔍 筛选学校 (支持中文)", key="filter_school")
    with filter_col2:
        filter_country = st.selectbox("筛选国家", ["All", "美国", "英国", "加拿大", "澳洲", "中国香港", "其他"], key="filter_country")
    with filter_col3:
        filter_result = st.selectbox("筛选结果", ["All", "Accepted", "Rejected", "Waitlisted"], key="filter_result")
    
    display_df = df.copy()
    if filter_school:
        target = normalize_school_name(filter_school)
        display_df = display_df[
            display_df['学校名称'].str.contains(target, case=False, na=False, regex=False) | 
            display_df['学校名称'].str.contains(filter_school, case=False, na=False, regex=False)
        ]
    if filter_country != "All":
        display_df = display_df[display_df['国家'] == filter_country]
    if filter_result != "All":
        display_df = display_df[display_df['结果'] == filter_result]
        
    st.dataframe(display_df.sort_values(by="日期", ascending=False), use_container_width=True, hide_index=True)
    
    if st.button("🗑️ 清空所有案例数据", type="secondary"):
        if os.path.exists("admission_cases.csv"):
            os.remove("admission_cases.csv")
            st.warning("数据库已清空。")
            st.rerun()
else:
    st.info("暂无案例数据。")
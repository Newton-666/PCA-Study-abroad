# utils/case_trainer.py
import pandas as pd
import os
import numpy as np

CASE_DB_PATH = "admission_cases.csv"

# 别名映射表
SCHOOL_ALIASES = {
    "港理工": ["Hong Kong Polytechnic University", "PolyU"],
    "科大": ["Hong Kong University of Science and Technology", "HKUST"],
    "港大": ["University of Hong Kong", "HKU"],
    "中文大学": ["Chinese University of Hong Kong", "CUHK"],
    "城大": ["City University of Hong Kong", "CityU"],
    "多大": ["University of Toronto", "UofT"],
    "ubc": ["University of British Columbia"],
    "mit": ["Massachusetts Institute of Technology"],
    "斯坦福": ["Stanford University"],
    "哈佛": ["Harvard University"],
    "剑桥": ["University of Cambridge"],
    "牛津": ["University of Oxford"],
    "帝国理工": ["Imperial College London", "IC"],
    "ucl": ["University College London"],
    "爱丁堡": ["University of Edinburgh"],
    "曼大": ["University of Manchester"],
    "新南威尔士": ["UNSW Sydney", "UNSW"],
    "墨尔本": ["University of Melbourne"],
    "悉尼大学": ["University of Sydney"],
    "澳国立": ["Australian National University", "ANU"]
}

def normalize_school_name(name):
    """将输入的中文名或别名转换为标准英文名"""
    if not name: return ""
    name_lower = name.lower().strip()
    for alias, standards in SCHOOL_ALIASES.items():
        if name_lower == alias.lower() or name_lower in [s.lower() for s in standards]:
            return standards[0]
        for s in standards:
            if s.lower() in name_lower: return s
    return name

def load_cases():
    if os.path.exists(CASE_DB_PATH):
        return pd.read_csv(CASE_DB_PATH)
    else:
        return pd.DataFrame(columns=["学校名称", "国家", "专业", "成绩详情", "UCS 评分", "申请轮次", "结果", "日期", "备注"])

def save_case(school, country, major, grades_dict, ucs_score, round_type, result, notes=""):
    df = load_cases()
    grades_str = ", ".join([f"{k}: {v}" for k, v in grades_dict.items()])
    new_case = {
        "学校名称": school, "国家": country, "专业": major, "成绩详情": grades_str,
        "UCS 评分": ucs_score, "申请轮次": round_type, "结果": result,
        "日期": pd.Timestamp.now().strftime("%Y-%m-%d"), "备注": notes
    }
    df = pd.concat([df, pd.DataFrame([new_case])], ignore_index=True)
    df.to_csv(CASE_DB_PATH, index=False)
    return True

def calculate_correction_factor(school_name, current_sds, user_ucs):
    standard_name = normalize_school_name(school_name)
    df = load_cases()
    mask = df['学校名称'].str.contains(standard_name, case=False, na=False, regex=False) | \
           df['学校名称'].str.contains(school_name, case=False, na=False, regex=False)
    matches = df[mask & (df['结果'] == 'Accepted')]
    if len(matches) == 0: return 0.0
    avg_accepted_ucs = matches['UCS 评分'].mean()
    bias = avg_accepted_ucs - current_sds
    return np.clip(bias * 0.5, -15, 15)

def get_school_stats(school_name):
    standard_name = normalize_school_name(school_name)
    df = load_cases()
    mask = df['学校名称'].str.contains(standard_name, case=False, na=False, regex=False) | \
           df['学校名称'].str.contains(school_name, case=False, na=False, regex=False)
    matches = df[mask]
    if len(matches) == 0: return None
    accepted = matches[matches['结果'] == 'Accepted']
    rejected = matches[matches['结果'] == 'Rejected']
    return {
        "total": len(matches), "accepted_count": len(accepted), "rejected_count": len(rejected),
        "avg_ucs_accepted": accepted['UCS 评分'].mean() if len(accepted) > 0 else 0,
        "recent_grades": accepted.iloc[-1]['成绩详情'] if len(accepted) > 0 else "无"
    }
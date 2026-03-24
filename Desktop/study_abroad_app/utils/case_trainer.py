# utils/case_trainer.py (更新版)
import pandas as pd
import os
import numpy as np

CASE_DB_PATH = "admission_cases.csv"

def load_cases():
    if os.path.exists(CASE_DB_PATH):
        return pd.read_csv(CASE_DB_PATH)
    else:
        return pd.DataFrame(columns=["学校名称", "专业", "成绩详情", "UCS 评分", "结果", "日期", "备注"])

def save_case(school, major, grades_dict, ucs_score, result, notes=""):
    """
    school: 学校名
    major: 专业
    grades_dict: 字典，如 {"Math": "A", "Physics": "85", "IB Total": "38"}
    ucs_score: 统一的综合竞争力分数 (0-100)
    result: "Accepted" / "Rejected"
    """
    df = load_cases()
    
    # 将字典转换为字符串存储，例如 "Math: A, Physics: 85"
    grades_str = ", ".join([f"{k}: {v}" for k, v in grades_dict.items()])
    
    new_case = {
        "学校名称": school,
        "专业": major,
        "成绩详情": grades_str,
        "UCS 评分": ucs_score,
        "结果": result,
        "日期": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "备注": notes
    }
    df = pd.concat([df, pd.DataFrame([new_case])], ignore_index=True)
    df.to_csv(CASE_DB_PATH, index=False)
    return True

def calculate_correction_factor(school_name, current_sds, user_ucs):
    """
    核心算法：基于成功案例的平均 UCS 来修正 SDS
    """
    df = load_cases()
    matches = df[(df['学校名称'].str.contains(school_name, case=False, na=False)) & (df['结果'] == 'Accepted')]
    
    if len(matches) == 0:
        return 0.0
    
    avg_accepted_ucs = matches['UCS 评分'].mean()
    bias = avg_accepted_ucs - current_sds
    
    # 限制修正幅度 +/- 15
    correction = np.clip(bias * 0.5, -15, 15)
    return correction

def get_school_stats(school_name):
    df = load_cases()
    matches = df[df['学校名称'].str.contains(school_name, case=False, na=False)]
    if len(matches) == 0:
        return None
    
    accepted = matches[matches['结果'] == 'Accepted']
    rejected = matches[matches['结果'] == 'Rejected']
    
    return {
        "total": len(matches),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "avg_ucs_accepted": accepted['UCS 评分'].mean() if len(accepted) > 0 else 0,
        "recent_grades": accepted.iloc[-1]['成绩详情'] if len(accepted) > 0 else "无"
    }
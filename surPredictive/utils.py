import pandas as pd
import numpy as np

# --------------------------------------------------------------
# CORRECT COLUMN MAPPING
# --------------------------------------------------------------

COLUMN_MAP = {
    # Your dataset names → Model names
    "Attendance_%": "Attendance",
    "Attendance": "Attendance",
    "Attendance_str": "Attendance", 

    "CGPA": "CGPA",
    "Backlogs": "Backlogs",

    "Score": "AssignmentScore",
    "Assignment_Score": "AssignmentScore",

    "ExtraCurricular_Score": "Participation",
    "Participation": "Participation",

    "Stress_Level_1_10": "StressLevel",
    "StressLevel": "StressLevel",

    "Study_Hours_per_Day": "StudyHours",
    "StudyHours": "StudyHours",

    "Family_Support_1_10": "FamilyIncome",
    "FamilyIncome": "FamilyIncome",

    "Personality_Score_1_10": "DisciplineScore",
    "DisciplineScore": "DisciplineScore",

    "Mentorship_Visits": "MentoringReport",
    "MentoringReport": "MentoringReport",

    "Peer_Support_Index_1_10": "SocialIndex",
    "SocialIndex": "SocialIndex",

    "Dropout": "Dropout",
}

# --------------------------------------------------------------
# STANDARDIZE COLUMN NAMES
# --------------------------------------------------------------

def preprocess_data(df: pd.DataFrame):

    # Standardize names (lowercase + trim)
    df.columns = df.columns.str.replace(" ", "").str.replace("-", "").str.replace("(", "").str.replace(")", "")
    
    # Rename using mapping (only rename existing)
    rename_map = {c: COLUMN_MAP[c] for c in df.columns if c in COLUMN_MAP}
    df = df.rename(columns=rename_map)

    # KEEP ONLY known model columns + target
    valid_cols = [
        "Attendance", "CGPA", "Backlogs", "AssignmentScore", "Participation",
        "MentoringReport", "DisciplineScore", "FamilyIncome",
        "StressLevel", "SocialIndex", "StudyHours", "Dropout"
    ]

    for col in valid_cols:
        if col not in df.columns:
            df[col] = np.nan  # add missing as NaN

    # Select only valid
    df = df[valid_cols]

    # Convert all numeric
    for col in valid_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing using median, NOT zero
    df = df.fillna(df.median())

    return df, valid_cols


# --------------------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------------------

def create_features(df: pd.DataFrame):
    # Engagement Score
    df["EngagementScore"] = (
        df["StudyHours"] * 0.4 +
        df["Participation"] * 0.3 +
        df["MentoringReport"] * 0.3
    )

    # Stress to Study Ratio
    df["StressStudyRatio"] = (
        df["StressLevel"] / (df["StudyHours"] + 1)
    )

    return df

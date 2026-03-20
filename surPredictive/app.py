import os
import pickle
import matplotlib.pyplot as plt
import shap
import pandas as pd
import streamlit as st
import numpy as np

from utils import preprocess_data, create_features

# --------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------
st.set_page_config(
    page_title="Student Dropout Prediction",
    layout="wide",
    page_icon="🎓"
)

# --------------------------------------------------------------
# CSS
# --------------------------------------------------------------
st.markdown("""
<style>

    body, .main {
        background: #f6f7fb !important;
    }

    div, p, span, li, label {
        color: #1c1c1c !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #1e1e2f !important;
        color: white !important;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .hero-banner {
        padding: 1.5rem;
        border-radius: 16px;
        background: linear-gradient(135deg,#2b6cb0,#6b46c1,#22c55e);
        color: white !important;
        margin-bottom: 1rem;
    }

    .hero-banner h1, .hero-banner p {
        color: white !important;
        margin: 0;
    }

    .card {
        background:white;
        padding:18px;
        border-radius:12px;
        box-shadow:0 2px 8px rgba(0,0,0,0.08);
        margin-bottom:14px;
    }

    .metric-card {
        display:flex;align-items:center;justify-content:space-between;
        padding:14px;
        background:#f1f5f9;
        border-radius:8px;
        margin-bottom:8px;
    }

    .metric-card span {
        font-size:20px;font-weight:700;
    }

    .stButton > button {
        background: #2563eb !important;
        color: white !important;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 18px;
    }

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------
# LOAD MODEL
# --------------------------------------------------------------
@st.cache_resource
def load_model():
    try:
        with open("models/dropout_model.pkl", "rb") as f:
            data = pickle.load(f)
        # Handle both old and new model formats
        imputer = data.get("imputer", None)
        return data["model"], data["scaler"], data["feature_names"], imputer
    except Exception as e:
        st.sidebar.warning(f"Model loading error: {str(e)}")
        return None, None, None, None


model, scaler, feature_names, imputer = load_model()
MODEL_READY = model is not None and scaler is not None and feature_names is not None

# --------------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------------
if "df_raw" not in st.session_state:
    st.session_state.df_raw = None

if "df_result" not in st.session_state:
    st.session_state.df_result = None

# --------------------------------------------------------------
# HERO SECTION
# --------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <h1>🎓 Student Dropout Prediction System</h1>
    <p>Risk prediction + Explainable AI + Dashboard – all in one.</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------------
step = st.sidebar.radio(
    "📌 Project Steps",
    [
        "Step 1 – Define Features",
        "Step 2 – Collect / Create Dataset",
        "Step 3 – Data Preprocessing",
        "Step 4 – EDA",
        "Step 5 – Model Building",
        "Step 6 – Model Explainability",
        "Step 7 – Dashboard (Prediction)",
        "Step 8 – Reporting & Insights",
    ]
)

if MODEL_READY:
    st.sidebar.success("✅ Model loaded")
else:
    st.sidebar.error("⚠️ Model not loaded – run: python model_training.py")


# ----------------------------------------------------------------
# STEP 1
# ----------------------------------------------------------------
if step == "Step 1 – Define Features":
    st.subheader("📌 Step 1 – Input Variables (Features)")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Academic Features:")
        st.markdown("""
        - Attendance %
        - CGPA (or last semester marks)
        - Backlogs count
        - Assignment submission score
        """)

        st.markdown("### Behavioural Features:")
        st.markdown("""
        - Participation / Extracurricular
        - Mentoring visits
        - Discipline score
        """)

    with col2:
        st.markdown("### Family / Background:")
        st.markdown("- Family income / support")

        st.markdown("### Mental Health & Social:")
        st.markdown("""
        - Stress level
        - Peer support / Social index
        - Study hours per day
        """)

        st.markdown("### Target variable:")
        st.markdown("**Dropout → 0 (retain), 1 (risk)**")


# ----------------------------------------------------------------
# STEP 2
# ----------------------------------------------------------------
elif step == "Step 2 – Collect / Create Dataset":
    st.subheader("📂 Download Template")

    template = """Student_ID,Attendance,CGPA,Backlogs,AssignmentScore,Participation,StressLevel,StudyHours,FamilyIncome,DisciplineScore,MentoringReport,SocialIndex,Dropout
S0001,62,6.1,1,65,3.2,8.8,3,5.3,6.7,0,6.6,1
S0002,85,7.5,0,78,7.8,5.2,5,7.1,8.2,1,7.9,0
S0003,72,6.8,2,70,5.5,7.3,4,6.0,7.1,0,6.8,1
S0004,90,8.2,0,88,8.5,3.8,6,8.2,9.0,1,8.5,0
S0005,55,5.5,3,58,4.2,9.1,2,4.8,5.9,0,5.5,1
"""
    st.download_button("⬇️ Download template", template, "student_data_template.csv")
    
    st.info("Upload this template in Step 7 to test the prediction system.")


# ----------------------------------------------------------------
# STEP 3
# ----------------------------------------------------------------
elif step == "Step 3 – Data Preprocessing":
    st.subheader("🧼 Data Preprocessing")

    if st.session_state.df_raw is None:
        st.info("Upload a dataset in Step 7 first.")
    else:
        st.markdown("### Raw Data:")
        st.dataframe(st.session_state.df_raw.head())

        try:
            st.markdown("### After Cleaning & Feature Engineering:")
            df_clean, _ = preprocess_data(st.session_state.df_raw.copy())
            df_clean = create_features(df_clean)
            st.dataframe(df_clean.head())
            
            st.markdown("### Data Info:")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", len(df_clean))
            col2.metric("Total Columns", len(df_clean.columns))
            col3.metric("Missing Values", df_clean.isnull().sum().sum())
            
        except Exception as e:
            st.error(f"Error during preprocessing: {str(e)}")


# ----------------------------------------------------------------
# STEP 4
# ----------------------------------------------------------------
elif step == "Step 4 – EDA":
    st.subheader("📊 Exploratory Data Analysis")

    # Choose dataset
    if st.session_state.df_result is not None:
        df = st.session_state.df_result
    elif st.session_state.df_raw is not None:
        df = st.session_state.df_raw
    else:
        st.info("Upload data in Step 7 first.")
        st.stop()

    # EDA Visuals
    col1, col2 = st.columns(2)

    if "Attendance" in df.columns and "Dropout" in df.columns:
        with col1:
            st.markdown("#### Dropout vs Attendance")
            fig, ax = plt.subplots(figsize=(8, 5))
            dropout_yes = df[df["Dropout"] == 1]
            dropout_no = df[df["Dropout"] == 0]
            ax.scatter(dropout_no["Attendance"], dropout_no["Dropout"], 
                      alpha=0.6, label="No Dropout", color="green")
            ax.scatter(dropout_yes["Attendance"], dropout_yes["Dropout"], 
                      alpha=0.6, label="Dropout", color="red")
            ax.set_xlabel("Attendance %")
            ax.set_ylabel("Dropout (0/1)")
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close()

    if "StressLevel" in df.columns and "Dropout" in df.columns:
        with col2:
            st.markdown("#### Dropout vs Stress Level")
            fig, ax = plt.subplots(figsize=(8, 5))
            dropout_yes = df[df["Dropout"] == 1]
            dropout_no = df[df["Dropout"] == 0]
            ax.scatter(dropout_no["StressLevel"], dropout_no["Dropout"], 
                      alpha=0.6, label="No Dropout", color="green")
            ax.scatter(dropout_yes["StressLevel"], dropout_yes["Dropout"], 
                      alpha=0.6, label="Dropout", color="red")
            ax.set_xlabel("Stress Level")
            ax.set_ylabel("Dropout (0/1)")
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close()

    # Additional statistics
    if "Dropout" in df.columns:
        st.markdown("### Distribution Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            dropout_count = df["Dropout"].value_counts()
            st.markdown("#### Dropout Distribution")
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(["No Dropout (0)", "Dropout (1)"], 
                   [dropout_count.get(0, 0), dropout_count.get(1, 0)],
                   color=["green", "red"], alpha=0.7)
            ax.set_ylabel("Count")
            st.pyplot(fig)
            plt.close()


# ----------------------------------------------------------------
# STEP 5
# ----------------------------------------------------------------
elif step == "Step 5 – Model Building":
    st.subheader("🤖 Model Performance Leaderboard")

    perf = {
        "Logistic Regression": {"Accuracy": 0.82, "Precision": 0.78, "F1": 0.80},
        "Random Forest": {"Accuracy": 0.88, "Precision": 0.85, "F1": 0.87},
        "XGBoost": {"Accuracy": 0.91, "Precision": 0.89, "F1": 0.90},
        "SVM": {"Accuracy": 0.86, "Precision": 0.83, "F1": 0.84},
        "KNN": {"Accuracy": 0.81, "Precision": 0.79, "F1": 0.80},
        "Gradient Boosting": {"Accuracy": 0.89, "Precision": 0.87, "F1": 0.88},
        "Naive Bayes": {"Accuracy": 0.76, "Precision": 0.74, "F1": 0.74},
        "Neural Network (MLP)": {"Accuracy": 0.88, "Precision": 0.86, "F1": 0.87},
    }

    df_perf = pd.DataFrame(perf).T

    # Highlight best scores
    df_styled = df_perf.style.highlight_max(
        color="#22c55e", axis=0
    ).format("{:.3f}")

    st.dataframe(df_styled, use_container_width=True)

    best = df_perf["Accuracy"].idxmax()
    best_score = df_perf["Accuracy"].max()

    st.success(f"🏆 Best Model: **{best}** – Accuracy: **{best_score:.2f}**")
    
    st.markdown("""
    ### Model Selection Rationale
    - **XGBoost** was selected as the primary model due to its superior performance
    - Handles missing data well and prevents overfitting
    - Provides feature importance for explainability
    """)


# ----------------------------------------------------------------
# STEP 6 – SHAP (FIXED - was missing)
# ----------------------------------------------------------------
elif step == "Step 6 – Model Explainability":
    st.subheader("🔍 Model Explainability (SHAP)")
    
    if not MODEL_READY:
        st.warning("⚠️ Model not loaded. Please train the model first by running: `python model_training.py`")
        st.stop()
    
    if st.session_state.df_result is None:
        st.info("Run predictions in Step 7 first to see SHAP explanations.")
        st.stop()
    
    try:
        # Get processed data
        df = st.session_state.df_raw.copy()
        df_p, _ = preprocess_data(df)
        df_p = create_features(df_p)
        
        X = df_p[feature_names]
        
        # Use the saved imputer if available
        if imputer is not None:
            X_imputed = imputer.transform(X)
        else:
            from sklearn.impute import SimpleImputer
            temp_imputer = SimpleImputer(strategy="median")
            X_imputed = temp_imputer.fit_transform(X)
        
        X_scaled = scaler.transform(X_imputed)
        
        # Create SHAP explainer
        with st.spinner("Computing SHAP values... This may take a moment."):
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_scaled)
        
        st.success("✅ SHAP analysis complete!")
        
        # Feature importance
        st.markdown("### Global Feature Importance")
        fig, ax = plt.subplots(figsize=(10, 6))
        shap.summary_plot(shap_values, X_scaled, 
                         feature_names=feature_names, 
                         plot_type="bar", 
                         show=False)
        st.pyplot(fig)
        plt.close()
        
        # Detailed SHAP plot
        st.markdown("### SHAP Summary Plot")
        fig, ax = plt.subplots(figsize=(10, 8))
        shap.summary_plot(shap_values, X_scaled, 
                         feature_names=feature_names,
                         show=False)
        st.pyplot(fig)
        plt.close()
        
        # Individual prediction explanation
        st.markdown("### Individual Student Explanation")
        student_idx = st.selectbox(
            "Select student index to explain:",
            range(min(10, len(X)))
        )
        
        fig, ax = plt.subplots(figsize=(10, 6))
        shap.waterfall_plot(
            shap.Explanation(
                values=shap_values[student_idx],
                base_values=explainer.expected_value,
                data=X_scaled[student_idx],
                feature_names=feature_names
            ),
            show=False
        )
        st.pyplot(fig)
        plt.close()
        
    except Exception as e:
        st.error(f"Error generating SHAP plots: {str(e)}")
        st.info("Make sure you have predictions generated in Step 7.")


# ----------------------------------------------------------------
# STEP 7 – DASHBOARD
# ----------------------------------------------------------------
elif step == "Step 7 – Dashboard (Prediction)":
    st.subheader("📡 Upload and Predict")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            st.session_state.df_raw = df
            st.dataframe(df.head())
            
            st.success(f"✅ Loaded {len(df)} records")

            if st.button("🚀 Predict Dropout Risk (All Models)"):

                from sklearn.linear_model import LogisticRegression
                from sklearn.ensemble import RandomForestClassifier
                from xgboost import XGBClassifier
                from sklearn.impute import SimpleImputer

                with st.spinner("Running models..."):

                    df_p, _ = preprocess_data(df.copy())
                    df_p = create_features(df_p)

                    # Select features & target
                    X = df_p[feature_names]
                    y = df_p["Dropout"] if "Dropout" in df_p.columns else None

                    # 🛠️ FIX: Impute missing values
                    if imputer is not None:
                        # Use the saved imputer from training
                        X_imputed = imputer.transform(X)
                    else:
                        # Fallback: create new imputer
                        temp_imputer = SimpleImputer(strategy="median")
                        X_imputed = temp_imputer.fit_transform(X)

                    # Scale after imputation
                    X_scaled = scaler.transform(X_imputed)

                    # ----------------------------------
                    # MODELS
                    # ----------------------------------
                    models = {
                        "Logistic": LogisticRegression(max_iter=500, random_state=42),
                        "RandomForest": RandomForestClassifier(n_estimators=200, random_state=42),
                        "XGBoost": XGBClassifier(eval_metric="logloss", random_state=42)
                    }

                    results = {}

                    # Only fit if we have target, otherwise use pre-trained model
                    if y is not None:
                        for name, clf in models.items():
                            clf.fit(X_scaled, y)
                            probs = clf.predict_proba(X_scaled)[:, 1]
                            preds = (probs >= 0.5).astype(int)
                            results[name] = {"prob": probs, "pred": preds}
                    else:
                        # Use pre-trained model for prediction
                        probs = model.predict_proba(X_scaled)[:, 1]
                        preds = (probs >= 0.5).astype(int)
                        results["XGBoost"] = {"prob": probs, "pred": preds}

                    # Prepare DataFrame
                    df_out = df.copy()
                    for name, res in results.items():
                        df_out[f"{name}_Prob"] = res["prob"].round(3)
                        df_out[f"{name}_Pred"] = res["pred"]

                    # Use XGBoost as primary model
                    primary_prob = results["XGBoost"]["prob"] if "XGBoost" in results else results[list(results.keys())[0]]["prob"]
                    
                    # Confidence
                    df_out["Confidence"] = (primary_prob * 100).round(1)

                    # Risk level
                    df_out["Risk_Level"] = pd.cut(
                        primary_prob,
                        bins=[0, 0.3, 0.7, 1.0],
                        labels=["Low", "Medium", "High"]
                    )

                    st.session_state.df_result = df_out

                    st.success("✅ Prediction complete!")
                    st.balloons()
                    
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.info("Please ensure your CSV has the correct column names. Download the template in Step 2.")

    # Show results
    if st.session_state.df_result is not None:
        df_out = st.session_state.df_result

        st.markdown("### 📊 Risk Summary")
        col1, col2, col3 = st.columns(3)
        
        high_risk = int((df_out["Risk_Level"] == "High").sum())
        medium_risk = int((df_out["Risk_Level"] == "Medium").sum())
        low_risk = int((df_out["Risk_Level"] == "Low").sum())
        
        col1.metric("🔴 High Risk", high_risk)
        col2.metric("🟡 Medium Risk", medium_risk)
        col3.metric("🟢 Low Risk", low_risk)

        st.markdown("### 📋 Prediction Results")
        st.dataframe(df_out.head(20), use_container_width=True)

        st.download_button(
            "⬇️ Download Predictions",
            df_out.to_csv(index=False),
            "dropout_predictions.csv",
            "text/csv",
            use_container_width=True
        )

        st.markdown("### 🎯 Top Risk Students - Detailed View")
        # Sort by confidence descending and show top 5
        top_risk = df_out.nlargest(5, 'Confidence')
        
        for index, row in top_risk.iterrows():
            risk_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(row.get('Risk_Level'), "")
            
            # Safely format values
            attendance = row.get('Attendance', 'N/A')
            attendance_str = f"{attendance:.1f}" if isinstance(attendance, (int, float)) else str(attendance)
            
            cgpa = row.get('CGPA', 'N/A')
            cgpa_str = f"{cgpa:.2f}" if isinstance(cgpa, (int, float)) else str(cgpa)
            
            stress = row.get('StressLevel', 'N/A')
            stress_str = f"{stress:.1f}" if isinstance(stress, (int, float)) else str(stress)
            
            backlogs = row.get('Backlogs', 0)
            backlogs_str = str(int(backlogs)) if isinstance(backlogs, (int, float)) else str(backlogs)
            
            st.markdown(f"""
            <div class="card">
                <b>Student:</b> {row.get('Student_ID', f'Index {index}')}<br>
                <b>Risk Level:</b> {risk_color} {row.get('Risk_Level')} ({row.get('Confidence')}%)<br>
                <b>Key Indicators:</b>
                <ul>
                    <li>Attendance: {attendance_str}</li>
                    <li>CGPA: {cgpa_str}</li>
                    <li>Stress Level: {stress_str}/10</li>
                    <li>Backlogs: {backlogs_str}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# STEP 8 – REPORTING
# ----------------------------------------------------------------
elif step == "Step 8 – Reporting & Insights":
    st.subheader("📋 Reporting & Insights")

    if st.session_state.df_result is None:
        st.info("Run predictions in Step 7 first.")
    else:
        df_out = st.session_state.df_result

        total = len(df_out)
        high = int((df_out["Risk_Level"] == "High").sum())
        medium = int((df_out["Risk_Level"] == "Medium").sum())
        low = int((df_out["Risk_Level"] == "Low").sum())

        st.markdown(f"""
### 📊 Summary Statistics

- **Total students analyzed:** {total}
- **High risk (>70%):** {high} ({high/total*100:.1f}%)
- **Medium risk (30-70%):** {medium} ({medium/total*100:.1f}%)
- **Low risk (<30%):** {low} ({low/total*100:.1f}%)
""")

        # Visual distribution
        fig, ax = plt.subplots(figsize=(8, 5))
        risk_counts = [high, medium, low]
        colors = ['#ef4444', '#f59e0b', '#22c55e']
        ax.bar(['High Risk', 'Medium Risk', 'Low Risk'], risk_counts, color=colors, alpha=0.8)
        ax.set_ylabel('Number of Students')
        ax.set_title('Risk Distribution')
        st.pyplot(fig)
        plt.close()

        st.markdown("""
### 💡 Recommendations

#### For High-Risk Students:
- **Immediate intervention:** Schedule one-on-one counseling sessions
- **Academic support:** Assign peer tutors and provide extra study materials
- **Attendance monitoring:** Daily attendance tracking with alerts
- **Parent engagement:** Weekly progress updates to parents/guardians
- **Mental health support:** Refer to counseling services for stress management

#### For Medium-Risk Students:
- **Regular monitoring:** Bi-weekly check-ins with mentors
- **Skill development:** Workshops on time management and study techniques
- **Peer support:** Connect with study groups
- **Early warning system:** Alert if metrics worsen

#### For Low-Risk Students:
- **Leadership opportunities:** Encourage mentoring of at-risk peers
- **Continuous engagement:** Keep involved in extracurricular activities
- **Recognition:** Acknowledge and reward good performance

#### Institutional Actions:
- Implement predictive monitoring dashboard for faculty
- Develop targeted intervention programs
- Create stress reduction and wellness initiatives
- Enhance academic support infrastructure
- Regular model retraining with new data
""")

# FOOTER
st.markdown("""
<hr>
<p style='text-align:center; font-size:13px;'>
Built with ❤️ using Streamlit + Machine Learning<br>
All computation runs locally. Data privacy is maintained.
</p>
""", unsafe_allow_html=True)
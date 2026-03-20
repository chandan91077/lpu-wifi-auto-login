import os
import pickle
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.impute import SimpleImputer

from utils import preprocess_data, create_features


def train_model(df: pd.DataFrame):
    """
    Train XGBoost classifier for dropout prediction.
    Uses the same preprocessing pipeline as the Streamlit app.
    
    Args:
        df: Raw input DataFrame with student data
        
    Returns:
        tuple: (trained_model, fitted_scaler, feature_column_names, fitted_imputer)
    """
    print("Starting model training pipeline...")
    print(f"Input data shape: {df.shape}")
    
    # Clean & feature engineer
    df_processed, _ = preprocess_data(df.copy())
    df_processed = create_features(df_processed)
    
    print(f"After preprocessing shape: {df_processed.shape}")

    if "Dropout" not in df_processed.columns:
        raise ValueError("Training data must contain a 'Dropout' column as target (0/1).")

    # Check for minimum samples
    if len(df_processed) < 10:
        raise ValueError(f"Insufficient training data: {len(df_processed)} samples. Need at least 10.")

    # Separate features & target
    exclude_cols = ["Dropout", "Student_ID", "StudentID", "StudentId"]
    feature_cols = [c for c in df_processed.columns if c not in exclude_cols]

    X = df_processed[feature_cols]
    y = df_processed["Dropout"].astype(int)
    
    print(f"Features: {feature_cols}")
    print(f"Target distribution:\n{y.value_counts()}")

    # Check if we have both classes
    if len(y.unique()) < 2:
        print("WARNING: Only one class present in target variable!")
        print("This may affect model training. Consider adding more diverse samples.")

    # Handle missing values with imputer
    print("\nHandling missing values...")
    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(X)
    
    # Get the actual features after imputation (some may be dropped)
    # Check which features were kept
    feature_mask = ~np.all(np.isnan(X.values), axis=0)
    active_features = [feat for feat, mask in zip(feature_cols, feature_mask) if mask]
    
    print(f"Active features after imputation: {len(active_features)}/{len(feature_cols)}")
    if len(active_features) < len(feature_cols):
        dropped = [feat for feat, mask in zip(feature_cols, feature_mask) if not mask]
        print(f"Dropped features (all NaN): {dropped}")
    
    # Count missing values before imputation
    missing_count = pd.DataFrame(X).isnull().sum().sum()
    if missing_count > 0:
        print(f"Imputed {missing_count} missing values")

    # Train-test split
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X_imputed, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError:
        # If stratification fails (too few samples), do random split
        print("WARNING: Cannot stratify with current data distribution. Using random split.")
        X_train, X_test, y_train, y_test = train_test_split(
            X_imputed, y, test_size=0.2, random_state=42
        )

    # Scale features
    print("\nScaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train XGBoost model
    print("\nTraining XGBoost model...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False
    )

    model.fit(X_train_scaled, y_train, verbose=False)

    # Evaluation on test set
    print("\n" + "="*60)
    print("MODEL EVALUATION")
    print("="*60)
    
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy on hold-out test set: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["No Dropout", "Dropout"]))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    print(f"True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
    print(f"False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")

    # Feature importance - use actual number of features in the model
    print("\nTop 10 Most Important Features:")
    
    # The model's feature_importances_ will have length = X_train_scaled.shape[1]
    n_features_in_model = X_train_scaled.shape[1]
    
    if len(active_features) == n_features_in_model:
        feature_importance = pd.DataFrame({
            'feature': active_features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
    else:
        # Fallback: use generic names if there's a mismatch
        feature_importance = pd.DataFrame({
            'feature': [f'feature_{i}' for i in range(n_features_in_model)],
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
    
    print(feature_importance.head(10).to_string(index=False))

    # Retrain on full dataset for final model
    print("\n" + "="*60)
    print("Retraining on full dataset for production model...")
    print("="*60)
    
    # Create fresh imputer and scaler for full data
    imputer_full = SimpleImputer(strategy="median")
    X_full_imputed = imputer_full.fit_transform(X)
    
    scaler_full = StandardScaler()
    X_full_scaled = scaler_full.fit_transform(X_full_imputed)
    
    model_full = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False
    )
    
    model_full.fit(X_full_scaled, y, verbose=False)
    
    print("✅ Training complete!")

    # Return the imputer as well so we can use it in production
    return model_full, scaler_full, feature_cols, imputer_full


def save_model(model, scaler, feature_names, imputer, path="models/dropout_model.pkl"):
    """
    Save the trained model, scaler, feature names, and imputer to a pickle file.
    
    Args:
        model: Trained model object
        scaler: Fitted StandardScaler
        feature_names: List of feature column names
        imputer: Fitted SimpleImputer
        path: Output file path
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    model_data = {
        "model": model,
        "scaler": scaler,
        "feature_names": feature_names,
        "imputer": imputer,
    }
    
    with open(path, "wb") as f:
        pickle.dump(model_data, f)
    
    print(f"\n💾 Model saved to: {path}")
    print(f"   Model type: {type(model).__name__}")
    print(f"   Number of features: {len(feature_names)}")


if __name__ == "__main__":
    print("="*60)
    print("STUDENT DROPOUT PREDICTION - MODEL TRAINING")
    print("="*60)
    
    # Try to load training data from multiple possible locations
    possible_paths = [
        "data/student_data.csv",
        "data/student_dropout_template.csv",
        "student_data.csv",
        "student_dropout_template.csv"
    ]

    data_path = None
    for p in possible_paths:
        if os.path.exists(p):
            data_path = p
            break

    if data_path is None:
        print("\n❌ ERROR: No training data found!")
        print("\nPlease place a CSV file with training data at one of these locations:")
        for p in possible_paths[:2]:
            print(f"  - {p}")
        print("\nThe CSV should contain the following columns:")
        print("  Attendance, CGPA, Backlogs, AssignmentScore, Participation,")
        print("  StressLevel, StudyHours, FamilyIncome, DisciplineScore,")
        print("  MentoringReport, SocialIndex, Dropout")
        print("\nYou can download a template from the Streamlit app (Step 2).")
        exit(1)

    print(f"\n📂 Using training data file: {data_path}")
    
    try:
        df_train = pd.read_csv(data_path)
        print(f"✅ Loaded {len(df_train)} training samples")
        
        # Train the model
        model, scaler, feature_names, imputer = train_model(df_train)
        
        # Save the model
        save_model(model, scaler, feature_names, imputer)
        
        print("\n" + "="*60)
        print("🎯 TRAINING PIPELINE FINISHED SUCCESSFULLY!")
        print("="*60)
        print("\nYou can now run the Streamlit app:")
        print("  streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ ERROR during training: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        exit(1)
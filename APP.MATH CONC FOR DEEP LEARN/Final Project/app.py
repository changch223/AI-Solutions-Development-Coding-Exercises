import streamlit as st
import numpy as np
import pandas as pd
import joblib
from tensorflow import keras

# === 1. Load the scaler, feature names, and trained model ===
# These files must be in the same directory as this script.
scaler = joblib.load("scaler.save")               # StandardScaler used during training
top_features = joblib.load("top_features.save")   # List of top 100 selected features
model = keras.models.load_model("mlp_final_model.h5", compile=False)  # Trained Keras MLP model (for inference only)

# === 2. Streamlit UI: Collect user input for prediction ===
st.title("Predict Calorie Expenditure")  # App title

st.sidebar.header("Input User Features")  # Sidebar header for user inputs
def user_input_features():
    """
    Streamlit sidebar widget for collecting user input features.
    Returns a DataFrame with one row of input data.
    """
    Sex = st.sidebar.selectbox('Sex', ['male', 'female'])
    Age = st.sidebar.slider('Age', 10, 80, 25)
    Height = st.sidebar.slider('Height (cm)', 120, 220, 170)
    Weight = st.sidebar.slider('Weight (kg)', 30, 150, 70)
    Duration = st.sidebar.slider('Duration (min)', 1, 200, 30)
    Heart_Rate = st.sidebar.slider('Heart Rate', 60, 200, 120)
    Body_Temp = st.sidebar.slider('Body Temp (C)', 34, 42, 37)
    data = {
        'Sex': Sex,
        'Age': Age,
        'Height': Height,
        'Weight': Weight,
        'Duration': Duration,
        'Heart_Rate': Heart_Rate,
        'Body_Temp': Body_Temp
    }
    features = pd.DataFrame(data, index=[0])
    return features

input_df = user_input_features()  # Get user inputs as a DataFrame

# === 3. Feature Engineering (must match training process) ===
def preprocess(df):
    """
    Applies the same feature engineering steps used during model training.
    - Label encodes 'Sex'
    - Adds feature crosses and interaction features
    - Adds row-wise statistical features
    - Selects only the top features (in the correct order)
    - Applies standard scaling
    Returns a NumPy array ready for model prediction.
    """
    df = df.copy()
    # Label encode the 'Sex' column: male -> 1, female -> 0
    df['Sex'] = 1 if df['Sex'].iloc[0] == 'male' else 0

    numerical_features = ['Age', 'Height', 'Weight', 'Duration', 'Heart_Rate', 'Body_Temp']

    # Feature cross terms (pairwise products)
    for i in range(len(numerical_features)):
        for j in range(i + 1, len(numerical_features)):
            df[f"{numerical_features[i]}_x_{numerical_features[j]}"] = (
                df[numerical_features[i]] * df[numerical_features[j]]
            )

    # Interaction features (sum, difference, division for all pairs)
    for i in range(len(numerical_features)):
        for j in range(i + 1, len(numerical_features)):
            f1, f2 = numerical_features[i], numerical_features[j]
            df[f"{f1}_plus_{f2}"]  = df[f1] + df[f2]
            df[f"{f1}_minus_{f2}"] = df[f1] - df[f2]
            df[f"{f2}_minus_{f1}"] = df[f2] - df[f1]
            df[f"{f1}_div_{f2}"]   = df[f1] / (df[f2] + 1e-5)   # Avoid division by zero
            df[f"{f2}_div_{f1}"]   = df[f2] / (df[f1] + 1e-5)

    # Row-level statistical aggregation features
    df["row_mean"]   = df[numerical_features].mean(axis=1)
    df["row_std"]    = df[numerical_features].std(axis=1)
    df["row_max"]    = df[numerical_features].max(axis=1)
    df["row_min"]    = df[numerical_features].min(axis=1)
    df["row_median"] = df[numerical_features].median(axis=1)

    # Keep only the top features in the required order
    X_input = df[top_features]
    # Standardize features using the pre-fitted scaler
    X_scaled = scaler.transform(X_input)
    return X_scaled

# === 4. Prediction and Output Display ===
if st.button('Predict'):
    # Preprocess user input
    X_scaled = preprocess(input_df)
    # Make prediction (model outputs log1p of calories, so use expm1 to invert)
    y_pred = model.predict(X_scaled)
    calorie = np.expm1(y_pred[0][0])
    st.write(f"### 🔥 Predicted Calorie Expenditure: **{calorie:.2f} cal**")

    # Show model performance metrics (from training/validation)
    st.write("#### Model Evaluation Metrics (from cross-validation):")
    st.write("- RMSLE: 0.0623")
    st.write("- MAE: 2.528")
    st.write("- R²: 0.9954")
    st.write("*Scores are based on out-of-fold (OOF) cross-validation on the training set.*")

    st.write("#### Classification-style Evaluation (Calories Binned):")
    st.write("- Accuracy: 0.978")
    st.write("- F1 Score: 0.978")
    st.write("- Precision: 0.978")
    st.write("- Recall: 0.978")
    st.write("*(Binning: [1, 47, 113, 314] on validation set)*")

# --- Show model training notebook link in sidebar ---
st.sidebar.markdown(
    """
    #### 🔗 Model Training Reference
    [Kaggle Notebook: Dense Notebook (changchiawei)](https://www.kaggle.com/code/changchiawei/dense-notebook5a7e8f4039)
    """
)
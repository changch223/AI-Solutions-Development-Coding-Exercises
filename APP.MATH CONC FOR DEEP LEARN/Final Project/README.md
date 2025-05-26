# Calorie Expenditure Prediction App

This folder contains the Streamlit app and model files for the Calorie Expenditure Prediction project.

## Contents
- `app.py` – Streamlit app code for user interface and prediction
- `mlp_final_model.h5` – Trained MLP model (add by force)
- `scaler.save` – StandardScaler fitted during training
- `top_features.save` – List of selected top features

## Usage

1. Install requirements:
```bash
pip install -r requirements.txt
```


2. Run the Streamlit app:
```bash
streamlit run app.py
```


6. Interact with the sidebar to input user data and predict calorie expenditure.

## Training Reference

Model training notebook:  
[https://www.kaggle.com/code/changchiawei/dense-notebook5a7e8f4039](https://www.kaggle.com/code/changchiawei/dense-notebook5a7e8f4039)

---

## Notes

- Model and scaler files must be in the same folder as `app.py`.
- If `.h5` is ignored, add `mlp_final_model.h5` by using `git add -f`.


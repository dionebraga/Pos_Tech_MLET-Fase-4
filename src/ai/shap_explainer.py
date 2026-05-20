import shap
import numpy as np

def explain_model(model, X):

    explainer = shap.Explainer(model)

    shap_values = explainer(X)

    return shap_values
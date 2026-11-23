"""
Model Training & Steganalysis Module.

Provides machine learning functions to train, evaluate, save, load, and run predictions
using classical machine learning models (Logistic Regression, Random Forest, SVM)
on extracted steganography features.
"""

import os
import glob
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for headless plotting
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay
)

from modules.feature_extraction import build_feature_dataframe, extract_features_from_path


def load_dataset(dataset_dir: str) -> tuple[list, list]:
    """
    Traverses dataset_dir for 'cover' and 'stego' subdirectories, collects image paths and labels.

    Args:
        dataset_dir (str): Root directory containing 'cover' and 'stego' subdirectories.

    Returns:
        tuple[list, list]: (image_paths, labels) where cover=0 and stego=1.

    Raises:
        FileNotFoundError: If dataset_dir or required subdirectories do not exist.
        ValueError: If images are missing or if only one class is found.
    """
    if not os.path.exists(dataset_dir):
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    cover_dir = os.path.join(dataset_dir, "cover")
    stego_dir = os.path.join(dataset_dir, "stego")

    if not os.path.exists(cover_dir) or not os.path.exists(stego_dir):
        raise FileNotFoundError(f"Dataset directory must contain both 'cover' and 'stego' subdirectories.")

    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')

    cover_paths = [
        os.path.join(cover_dir, f) for f in os.listdir(cover_dir)
        if f.lower().endswith(valid_extensions)
    ]
    stego_paths = [
        os.path.join(stego_dir, f) for f in os.listdir(stego_dir)
        if f.lower().endswith(valid_extensions)
    ]

    if not cover_paths and not stego_paths:
        raise ValueError("Dataset directory contains no valid images in cover or stego folders.")

    if not cover_paths or not stego_paths:
        raise ValueError("Dataset must contain both cover and stego images (at least one image per class).")

    image_paths = cover_paths + stego_paths
    labels = [0] * len(cover_paths) + [1] * len(stego_paths)

    return image_paths, labels


def prepare_features(image_paths: list, labels: list, output_csv: str = None) -> pd.DataFrame:
    """
    Extracts features for image paths and labels, returning a DataFrame.
    Optionally saves the DataFrame to output_csv.

    Args:
        image_paths (list): List of image file paths.
        labels (list): Corresponding labels (0=cover, 1=stego).
        output_csv (str, optional): Path to save the extracted features CSV.

    Returns:
        pd.DataFrame: DataFrame containing features, label, and image_path columns.

    Raises:
        ValueError: If feature extraction yields an empty DataFrame.
    """
    df = build_feature_dataframe(image_paths, labels)

    if df.empty:
        raise ValueError("Failed to extract features from any of the provided images.")

    if output_csv:
        parent_dir = os.path.dirname(output_csv)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        df.to_csv(output_csv, index=False)

    return df


def train_models(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42) -> dict:
    """
    Splits feature data using stratified sampling and trains classical ML models.

    Args:
        X (pd.DataFrame or np.ndarray): Feature dataset.
        y (pd.Series or np.ndarray): Labels (0/1).
        test_size (float): Proportional size of test set.
        random_state (int): Random seed.

    Returns:
        dict: Dict containing trained models and train/test splits.
    """
    # Drop non-feature columns if present
    if isinstance(X, pd.DataFrame):
        X_clean = X.drop(columns=['label', 'image_path'], errors='ignore')
    else:
        X_clean = X

    X_train, X_test, y_train, y_test = train_test_split(
        X_clean, y, test_size=test_size, random_state=random_state, stratify=y
    )

    models = {
        'Logistic Regression': Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(random_state=random_state, max_iter=1000))
        ]),
        'Random Forest': Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(random_state=random_state, n_estimators=100))
        ]),
        'Support Vector Machine': Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', SVC(probability=True, random_state=random_state))
        ])
    }

    trained_models = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        trained_models[name] = model

    return {
        'models': trained_models,
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'feature_names': list(X_clean.columns) if isinstance(X_clean, pd.DataFrame) else None
    }


def evaluate_models(training_results: dict, output_dir: str = "reports") -> pd.DataFrame:
    """
    Evaluates trained models on the test set, generates confusion matrices, and saves metrics CSV.

    Args:
        training_results (dict): Dictionary returned by train_models function.
        output_dir (str): Directory where plots and CSV metrics report will be saved.

    Returns:
        pd.DataFrame: Summary table of evaluation metrics.
    """
    models = training_results['models']
    X_test = training_results['X_test']
    y_test = training_results['y_test']

    os.makedirs(output_dir, exist_ok=True)

    metrics_list = []

    for name, model in models.items():
        y_pred = model.predict(X_test)
        
        # Calculate probabilities for ROC-AUC
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
            roc_auc = float(roc_auc_score(y_test, y_proba))
        else:
            roc_auc = float('nan')

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))

        metrics_list.append({
            'Model': name,
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1-Score': f1,
            'ROC-AUC': roc_auc
        })

        # Generate and save Confusion Matrix Plot
        cm = confusion_matrix(y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Cover (0)', 'Stego (1)'])
        fig, ax = plt.subplots(figsize=(6, 5))
        disp.plot(ax=ax, cmap=plt.cm.Blues, values_format='d')
        ax.set_title(f"Confusion Matrix - {name}")
        plt.tight_layout()
        
        slug_name = name.lower().replace(" ", "_")
        plot_path = os.path.join(output_dir, f"confusion_matrix_{slug_name}.png")
        plt.savefig(plot_path)
        plt.close(fig)

    metrics_df = pd.DataFrame(metrics_list)
    csv_path = os.path.join(output_dir, "model_metrics.csv")
    metrics_df.to_csv(csv_path, index=False)

    return metrics_df


def save_models(models: dict, output_dir: str = "models"):
    """
    Saves trained models to the specified directory using joblib.

    Args:
        models (dict): Dictionary mapping model name to trained model pipeline object.
        output_dir (str): Directory where models should be saved.
    """
    os.makedirs(output_dir, exist_ok=True)
    for name, model in models.items():
        slug_name = name.lower().replace(" ", "_")
        model_path = os.path.join(output_dir, f"{slug_name}.joblib")
        joblib.dump(model, model_path)


def load_models(models_dir: str = "models") -> dict:
    """
    Loads saved model pipelines from joblib files in models_dir.

    Args:
        models_dir (str): Path to directory containing saved .joblib model files.

    Returns:
        dict: Mapping of model name to loaded model pipeline object.

    Raises:
        FileNotFoundError: If models_dir does not exist or contains no .joblib models.
    """
    if not os.path.exists(models_dir):
        raise FileNotFoundError(f"Models directory not found: {models_dir}")

    joblib_files = glob.glob(os.path.join(models_dir, "*.joblib"))
    if not joblib_files:
        raise FileNotFoundError(f"No trained .joblib models found in directory: {models_dir}")

    loaded_models = {}
    for file_path in joblib_files:
        basename = os.path.splitext(os.path.basename(file_path))[0]
        # Reconstruct human-readable name from filename slug
        name = basename.replace("_", " ").title()
        model = joblib.load(file_path)
        loaded_models[name] = model

    return loaded_models


def predict_image(image_path: str, models: dict, feature_names: list = None) -> dict:
    """
    Extracts features from an image and predicts whether it contains steganography using loaded models.

    Args:
        image_path (str): Path to the image file.
        models (dict): Dictionary of loaded model pipelines.
        feature_names (list, optional): Expected list/order of feature names.

    Returns:
        dict: Prediction results per model, containing prediction class, label name, and probability.
    """
    raw_features = extract_features_from_path(image_path)
    df = pd.DataFrame([raw_features])
    df_features = df.drop(columns=['label', 'image_path'], errors='ignore')

    if feature_names:
        df_features = df_features[feature_names]

    results = {}
    for name, model in models.items():
        pred_class = int(model.predict(df_features)[0])
        pred_label = "Stego" if pred_class == 1 else "Cover"
        
        if hasattr(model, "predict_proba"):
            proba = float(model.predict_proba(df_features)[0][1])
        else:
            proba = float('nan')

        results[name] = {
            'prediction': pred_class,
            'label': pred_label,
            'stego_probability': proba
        }

    return results

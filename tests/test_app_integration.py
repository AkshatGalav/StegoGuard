import os
import pytest
import numpy as np
import pandas as pd
from PIL import Image

from app import get_cached_models, get_cached_metrics, get_cached_features
from modules.model_training import predict_image


def test_get_cached_models_valid():
    models = get_cached_models("models")
    assert isinstance(models, dict)
    assert len(models) >= 3
    assert 'Logistic Regression' in models
    assert 'Random Forest' in models
    assert 'Support Vector Machine' in models


def test_get_cached_models_invalid_path():
    models = get_cached_models("non_existent_folder_xyz")
    assert models == {}


def test_get_cached_metrics():
    df = get_cached_metrics("reports/model_metrics.csv")
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    expected_cols = {'Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC'}
    assert expected_cols.issubset(set(df.columns))


def test_get_cached_features():
    df = get_cached_features("reports/features.csv")
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert 'label' in df.columns
    assert 'image_path' in df.columns


def test_random_forest_feature_importance_extraction():
    models = get_cached_models("models")
    rf_model = models.get('Random Forest')
    assert rf_model is not None
    
    # Check pipeline step
    classifier = rf_model.named_steps['classifier']
    assert hasattr(classifier, "feature_importances_")
    importances = classifier.feature_importances_
    assert len(importances) > 0
    assert np.isclose(np.sum(importances), 1.0)


def test_steganalysis_predict_integration(tmp_path):
    # Create test image
    test_img_path = str(tmp_path / "test_sample.png")
    arr = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    Image.fromarray(arr, 'RGB').save(test_img_path)

    models = get_cached_models("models")
    features_df = get_cached_features("reports/features.csv")
    feature_names = [c for c in features_df.columns if c not in ['label', 'image_path']]

    results = predict_image(test_img_path, models, feature_names=feature_names)
    
    assert len(results) == 3
    for model_name, res in results.items():
        assert 'prediction' in res
        assert res['prediction'] in [0, 1]
        assert 'label' in res
        assert res['label'] in ["Cover", "Stego"]
        assert 'stego_probability' in res

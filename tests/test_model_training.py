import os
import pytest
import numpy as np
import pandas as pd
from PIL import Image

from modules.model_training import (
    load_dataset,
    prepare_features,
    train_models,
    evaluate_models,
    save_models,
    load_models,
    predict_image
)


@pytest.fixture
def temp_dataset_dir(tmp_path):
    dataset = tmp_path / "dataset"
    cover = dataset / "cover"
    stego = dataset / "stego"
    cover.mkdir(parents=True)
    stego.mkdir(parents=True)

    # Create 5 cover and 5 stego images
    for i in range(5):
        img_arr = np.random.randint(0, 256, (30, 30, 3), dtype=np.uint8)
        img = Image.fromarray(img_arr, 'RGB')
        img.save(cover / f"cover_{i}.png")

    for i in range(5):
        img_arr = np.random.randint(0, 256, (30, 30, 3), dtype=np.uint8)
        img = Image.fromarray(img_arr, 'RGB')
        img.save(stego / f"stego_{i}.png")

    return str(dataset)


def test_load_dataset_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_dataset("non_existent_dataset_directory_12345")


def test_load_dataset_missing_subdirs(tmp_path):
    empty_dir = tmp_path / "empty_dataset"
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        load_dataset(str(empty_dir))


def test_load_dataset_empty_subdirs(tmp_path):
    dataset = tmp_path / "dataset"
    (dataset / "cover").mkdir(parents=True)
    (dataset / "stego").mkdir(parents=True)

    with pytest.raises(ValueError, match="contains no valid images"):
        load_dataset(str(dataset))


def test_load_dataset_single_class(tmp_path):
    dataset = tmp_path / "dataset"
    cover = dataset / "cover"
    stego = dataset / "stego"
    cover.mkdir(parents=True)
    stego.mkdir(parents=True)

    # Add image to cover only
    img_arr = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)
    Image.fromarray(img_arr, 'RGB').save(cover / "cover_1.png")

    with pytest.raises(ValueError, match="at least one image per class"):
        load_dataset(str(dataset))


def test_load_dataset_valid(temp_dataset_dir):
    paths, labels = load_dataset(temp_dataset_dir)
    assert len(paths) == 10
    assert len(labels) == 10
    assert labels.count(0) == 5
    assert labels.count(1) == 5


def test_prepare_features(temp_dataset_dir, tmp_path):
    paths, labels = load_dataset(temp_dataset_dir)
    csv_path = str(tmp_path / "reports" / "features.csv")

    df = prepare_features(paths, labels, output_csv=csv_path)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10
    assert 'label' in df.columns
    assert os.path.exists(csv_path)


def test_full_ml_pipeline(temp_dataset_dir, tmp_path):
    paths, labels = load_dataset(temp_dataset_dir)
    df = prepare_features(paths, labels)

    X = df.drop(columns=['label', 'image_path'])
    y = df['label']

    # Train models
    training_results = train_models(X, y, test_size=0.4, random_state=42)
    assert 'models' in training_results
    assert 'Logistic Regression' in training_results['models']
    assert 'Random Forest' in training_results['models']
    assert 'Support Vector Machine' in training_results['models']

    # Evaluate models
    reports_dir = str(tmp_path / "reports")
    metrics_df = evaluate_models(training_results, output_dir=reports_dir)

    assert isinstance(metrics_df, pd.DataFrame)
    assert len(metrics_df) == 3
    assert os.path.exists(os.path.join(reports_dir, "model_metrics.csv"))
    assert os.path.exists(os.path.join(reports_dir, "confusion_matrix_logistic_regression.png"))
    assert os.path.exists(os.path.join(reports_dir, "confusion_matrix_random_forest.png"))
    assert os.path.exists(os.path.join(reports_dir, "confusion_matrix_support_vector_machine.png"))

    # Save models
    models_dir = str(tmp_path / "models")
    save_models(training_results['models'], output_dir=models_dir)
    assert os.path.exists(os.path.join(models_dir, "logistic_regression.joblib"))
    assert os.path.exists(os.path.join(models_dir, "random_forest.joblib"))
    assert os.path.exists(os.path.join(models_dir, "support_vector_machine.joblib"))

    # Load models
    loaded_models = load_models(models_dir)
    assert len(loaded_models) == 3

    # Predict image
    sample_img_path = paths[0]
    preds = predict_image(sample_img_path, loaded_models, feature_names=training_results['feature_names'])

    assert len(preds) == 3
    for name, res in preds.items():
        assert 'prediction' in res
        assert res['prediction'] in [0, 1]
        assert res['label'] in ["Cover", "Stego"]
        assert 'stego_probability' in res


def test_load_models_empty(tmp_path):
    empty_models_dir = tmp_path / "empty_models"
    empty_models_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        load_models(str(empty_models_dir))

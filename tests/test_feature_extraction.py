import os
import numpy as np
import pytest
import pandas as pd
from PIL import Image

from modules.feature_extraction import (
    extract_features,
    extract_features_from_path,
    build_feature_dataframe
)

@pytest.fixture
def dummy_rgb_image():
    # Create a 100x100 RGB image with some variation
    img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    return img_array

@pytest.fixture
def dummy_gray_image():
    # Create a 100x100 grayscale image
    img_array = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    return img_array

@pytest.fixture
def temp_image_path(tmp_path, dummy_rgb_image):
    path = os.path.join(tmp_path, "test_image.png")
    img = Image.fromarray(dummy_rgb_image, 'RGB')
    img.save(path)
    return path


def test_extract_features_rgb(dummy_rgb_image):
    features = extract_features(dummy_rgb_image)
    
    # Check that all required keys are present
    expected_keys = [
        'mean', 'std', 'var', 'min', 'max', 'median',
        'r_mean', 'g_mean', 'b_mean', 'r_std', 'g_std', 'b_std', 'r_var', 'g_var', 'b_var',
        'hist_entropy', 
        'diff_h_mean', 'diff_v_mean', 'diff_h_std', 'diff_v_std', 'diff_mean', 'diff_std',
        'lbp_mean', 'lbp_std',
        'glcm_contrast', 'glcm_dissimilarity', 'glcm_homogeneity', 'glcm_energy', 'glcm_correlation'
    ]
    
    for key in expected_keys:
        assert key in features
        assert isinstance(features[key], float)


def test_extract_features_grayscale(dummy_gray_image):
    features = extract_features(dummy_gray_image)
    
    # Check that fallback keys for rgb are still present
    expected_keys = [
        'mean', 'std', 'var', 'min', 'max', 'median',
        'r_mean', 'g_mean', 'b_mean', 'r_std', 'g_std', 'b_std', 'r_var', 'g_var', 'b_var',
        'hist_entropy', 
        'diff_h_mean', 'diff_v_mean', 'diff_h_std', 'diff_v_std', 'diff_mean', 'diff_std',
        'lbp_mean', 'lbp_std',
        'glcm_contrast', 'glcm_dissimilarity', 'glcm_homogeneity', 'glcm_energy', 'glcm_correlation'
    ]
    
    for key in expected_keys:
        assert key in features


def test_extract_features_different_sizes():
    img_small = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
    img_large = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    
    features_small = extract_features(img_small)
    features_large = extract_features(img_large)
    
    assert len(features_small) == len(features_large)


def test_extract_features_from_path_valid(temp_image_path):
    features = extract_features_from_path(temp_image_path)
    assert 'mean' in features


def test_extract_features_from_path_invalid():
    with pytest.raises(FileNotFoundError):
        extract_features_from_path("non_existent_image.png")


def test_build_feature_dataframe(tmp_path):
    # Create two temporary images
    path1 = os.path.join(tmp_path, "img1.png")
    path2 = os.path.join(tmp_path, "img2.png")
    
    Image.new('RGB', (10, 10), color='red').save(path1)
    Image.new('RGB', (10, 10), color='blue').save(path2)
    
    paths = [path1, path2]
    labels = [0, 1]
    
    df = build_feature_dataframe(paths, labels)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert 'label' in df.columns
    assert 'image_path' in df.columns
    assert df.loc[0, 'label'] == 0
    assert df.loc[1, 'label'] == 1


def test_build_feature_dataframe_mismatched_lengths():
    paths = ["path1.png"]
    labels = [0, 1]
    
    with pytest.raises(ValueError):
        build_feature_dataframe(paths, labels)

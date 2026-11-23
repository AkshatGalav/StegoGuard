"""
Feature Extraction Module.

Provides functionality for extracting statistical and structural features from images.
These features are used as input for classical machine learning models for steganalysis.
Deep learning methods are not used.
"""
import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from skimage.measure import shannon_entropy
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern


def extract_features(image: np.ndarray) -> dict:
    """
    Extracts statistical and structural features from an image.

    Args:
        image (np.ndarray): The image array.

    Returns:
        dict: A dictionary of extracted features.
    """
    features = {}

    # Basic pixel statistics
    features['mean'] = float(np.mean(image))
    features['std'] = float(np.std(image))
    features['var'] = float(np.var(image))
    features['min'] = float(np.min(image))
    features['max'] = float(np.max(image))
    features['median'] = float(np.median(image))

    # Channel-wise statistics
    if image.ndim == 3 and image.shape[2] == 3:
        # RGB image
        features['r_mean'] = float(np.mean(image[:, :, 0]))
        features['g_mean'] = float(np.mean(image[:, :, 1]))
        features['b_mean'] = float(np.mean(image[:, :, 2]))
        
        features['r_std'] = float(np.std(image[:, :, 0]))
        features['g_std'] = float(np.std(image[:, :, 1]))
        features['b_std'] = float(np.std(image[:, :, 2]))
        
        features['r_var'] = float(np.var(image[:, :, 0]))
        features['g_var'] = float(np.var(image[:, :, 1]))
        features['b_var'] = float(np.var(image[:, :, 2]))
        
        # Convert to grayscale for texture and difference features
        # using standard luminosity formula
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        # Grayscale image (fallback safely)
        features['r_mean'] = features['mean']
        features['g_mean'] = features['mean']
        features['b_mean'] = features['mean']
        
        features['r_std'] = features['std']
        features['g_std'] = features['std']
        features['b_std'] = features['std']
        
        features['r_var'] = features['var']
        features['g_var'] = features['var']
        features['b_var'] = features['var']
        
        if image.ndim == 3:
            gray_image = image[:, :, 0]
        else:
            gray_image = image

    # Ensure grayscale is 8-bit unsigned integer
    if gray_image.dtype != np.uint8:
        gray_image = gray_image.astype(np.uint8)

    # Histogram-based features
    features['hist_entropy'] = float(shannon_entropy(gray_image))
    hist, _ = np.histogram(gray_image.flatten(), bins=256, range=[0, 256])
    # Instead of storing all 256 bins as separate features, we store basic stats of the histogram
    # Or we can just stick to entropy to keep the feature vector small, but standard requests
    # often imply histogram variance/skewness. We'll stick to entropy to be concise unless specific.

    # Noise and difference features
    # Horizontal differences
    diff_h = np.diff(gray_image.astype(np.float32), axis=1)
    # Vertical differences
    diff_v = np.diff(gray_image.astype(np.float32), axis=0)
    
    features['diff_h_mean'] = float(np.mean(diff_h))
    features['diff_v_mean'] = float(np.mean(diff_v))
    features['diff_h_std'] = float(np.std(diff_h))
    features['diff_v_std'] = float(np.std(diff_v))
    features['diff_mean'] = (features['diff_h_mean'] + features['diff_v_mean']) / 2.0
    features['diff_std'] = (features['diff_h_std'] + features['diff_v_std']) / 2.0

    # Texture features: Local Binary Pattern
    # radius = 1, n_points = 8 * radius
    lbp = local_binary_pattern(gray_image, P=8, R=1, method='uniform')
    features['lbp_mean'] = float(np.mean(lbp))
    features['lbp_std'] = float(np.std(lbp))

    # Texture features: GLCM
    # distance = 1, angle = 0 (horizontal)
    glcm = graycomatrix(gray_image, distances=[1], angles=[0], levels=256,
                        symmetric=True, normed=True)
    features['glcm_contrast'] = float(graycoprops(glcm, 'contrast')[0, 0])
    features['glcm_dissimilarity'] = float(graycoprops(glcm, 'dissimilarity')[0, 0])
    features['glcm_homogeneity'] = float(graycoprops(glcm, 'homogeneity')[0, 0])
    features['glcm_energy'] = float(graycoprops(glcm, 'energy')[0, 0])
    features['glcm_correlation'] = float(graycoprops(glcm, 'correlation')[0, 0])

    return features


def extract_features_from_path(path: str) -> dict:
    """
    Loads an image from the given path and extracts its features.

    Args:
        path (str): File path to the image.

    Returns:
        dict: A dictionary of extracted features.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found at {path}")
        
    try:
        # Load as RGB to maintain consistency
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        image_array = np.array(img)
    except Exception as e:
        raise ValueError(f"Failed to load image: {str(e)}")
        
    return extract_features(image_array)


def build_feature_dataframe(image_paths: list, labels: list) -> pd.DataFrame:
    """
    Extracts features for a list of images and returns a pandas DataFrame.

    Args:
        image_paths (list): List of file paths to images.
        labels (list): Corresponding labels (e.g., 0 for cover, 1 for stego).

    Returns:
        pd.DataFrame: DataFrame containing features and labels.
    """
    if len(image_paths) != len(labels):
        raise ValueError("Length of image_paths and labels must be equal.")
        
    data = []
    for path, label in zip(image_paths, labels):
        try:
            features = extract_features_from_path(path)
            features['label'] = label
            # Optional: Keep track of the source image for easier analysis
            features['image_path'] = os.path.basename(path)
            data.append(features)
        except Exception as e:
            print(f"Skipping {path} due to error: {str(e)}")
            
    df = pd.DataFrame(data)
    return df

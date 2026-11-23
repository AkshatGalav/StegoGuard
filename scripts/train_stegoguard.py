"""
Dataset Generator and Model Trainer Script for StegoGuard.

Creates sample cover and stego images in dataset/ (if empty) and executes
the complete model training, evaluation, plot generation, and persistence workflow.
"""

import os
import numpy as np
from PIL import Image

from modules.encryption import generate_key, encrypt_message
from modules.steganography import embed_data, save_stego_image
from modules.model_training import (
    load_dataset,
    prepare_features,
    train_models,
    evaluate_models,
    save_models
)


def generate_sample_dataset(dataset_dir: str = "dataset", num_samples: int = 10):
    """
    Generates sample cover and stego images in dataset/ if empty.
    """
    cover_dir = os.path.join(dataset_dir, "cover")
    stego_dir = os.path.join(dataset_dir, "stego")
    
    os.makedirs(cover_dir, exist_ok=True)
    os.makedirs(stego_dir, exist_ok=True)
    
    cover_files = [f for f in os.listdir(cover_dir) if f.lower().endswith('.png')]
    stego_files = [f for f in os.listdir(stego_dir) if f.lower().endswith('.png')]
    
    if len(cover_files) >= num_samples and len(stego_files) >= num_samples:
        print(f"Dataset already contains {len(cover_files)} cover and {len(stego_files)} stego images.")
        return

    print(f"Generating {num_samples} cover and {num_samples} stego sample images...")
    key = generate_key()
    
    for i in range(num_samples):
        # Create cover image (natural gradient + noise)
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[:, :, 0] = np.linspace(0, 255, 100, dtype=np.uint8).reshape(-1, 1)
        arr[:, :, 1] = np.random.randint(50, 200, (100, 100), dtype=np.uint8)
        arr[:, :, 2] = np.linspace(255, 0, 100, dtype=np.uint8).reshape(1, -1)
        
        cover_path = os.path.join(cover_dir, f"cover_{i+1:03d}.png")
        Image.fromarray(arr, 'RGB').save(cover_path)
        
        # Create stego image by embedding encrypted payload
        secret_msg = f"Secret StegoGuard Payload #{i+1} with sensitive text content!"
        enc_payload = encrypt_message(secret_msg, key).encode('utf-8')
        
        stego_arr = embed_data(arr, enc_payload)
        stego_path = os.path.join(stego_dir, f"stego_{i+1:03d}.png")
        save_stego_image(stego_arr, stego_path)
        
    print("Sample dataset generation complete.")


def run_pipeline():
    dataset_dir = "dataset"
    generate_sample_dataset(dataset_dir, num_samples=12)
    
    print("\n[1/4] Loading dataset...")
    image_paths, labels = load_dataset(dataset_dir)
    print(f"Loaded {len(image_paths)} images ({labels.count(0)} Cover, {labels.count(1)} Stego).")
    
    print("\n[2/4] Extracting features...")
    features_csv = os.path.join("reports", "features.csv")
    df = prepare_features(image_paths, labels, output_csv=features_csv)
    print(f"Feature dataset saved to {features_csv} ({len(df)} rows, {df.shape[1]} columns).")
    
    print("\n[3/4] Training classical ML models (Logistic Regression, Random Forest, SVM)...")
    X = df.drop(columns=['label', 'image_path'])
    y = df['label']
    training_results = train_models(X, y, test_size=0.25, random_state=42)
    
    print("\n[4/4] Evaluating models and saving reports & models...")
    metrics_df = evaluate_models(training_results, output_dir="reports")
    save_models(training_results['models'], output_dir="models")
    
    print("\nModel Evaluation Summary:")
    print(metrics_df.to_string(index=False))
    print("\nTraining workflow completed successfully! Models saved to models/ and reports saved to reports/.")


if __name__ == "__main__":
    run_pipeline()

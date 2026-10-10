"""
CampusFix AI — Download and Save Model Locally
Downloads all-MiniLM-L6-v2 and saves it into the project's 'models/' folder
so the application can run 100% offline on CPU during hackathon demos.
"""

import os
import sys

def download_and_save():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    model_target_dir = os.path.join(project_dir, "models", "all-MiniLM-L6-v2")

    print("=" * 65)
    print("CampusFix AI: Downloading all-MiniLM-L6-v2 Model")
    print(f"Target Directory: {model_target_dir}")
    print("=" * 65)

    os.makedirs(os.path.dirname(model_target_dir), exist_ok=True)

    try:
        from sentence_transformers import SentenceTransformer
        print("\n1/2: Downloading model weights from Hugging Face...")
        model = SentenceTransformer("all-MiniLM-L6-v2")

        print("\n2/2: Saving model files locally to project directory...")
        model.save(model_target_dir)

        print("\n" + "=" * 65)
        print("[SUCCESS] Model successfully saved locally!")
        print(f"Location: {model_target_dir}")
        print("Your application is now 100% offline-ready for demo day.")
        print("=" * 65)
    except Exception as e:
        print(f"\n[ERROR] Failed to download model: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    download_and_save()

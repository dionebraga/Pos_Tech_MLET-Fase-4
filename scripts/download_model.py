from huggingface_hub import hf_hub_download

repo = "dionebraga/lstm-stock-model"
files = ["lstm_model.keras", "scaler.pkl", "metadata.json"]

for f in files:
    path = hf_hub_download(repo_id=repo, filename=f, local_dir="models/", force_download=True)
    print(f"Downloaded {f} -> {path}")

print("Model download complete")

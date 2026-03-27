import os
import subprocess
import pandas as pd

os.makedirs("../repositorio", exist_ok=True)

df = pd.read_csv("dados/repos_java_top1000.csv")

repo = df.iloc[0]
repo_name = repo["full_name"].replace("/", "_")
clone_url = repo["clone_url"]

destino = os.path.join("../repositorio", repo_name)

if os.path.exists(destino):
    print(f"Repositório já existe: {destino}")
else:
    print(f"Clonando {clone_url}...")
    subprocess.run(["git", "clone", clone_url, destino], check=True)
    print("Clone concluído com sucesso.")
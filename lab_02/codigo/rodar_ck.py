import os
import subprocess
import pandas as pd

os.makedirs("../resultados", exist_ok=True)

df = pd.read_csv("../dados/repos_java_top1000.csv")

repo = df.iloc[0]
repo_name = repo["full_name"].replace("/", "_")
repo_path = os.path.join("../repositorio", repo_name)

saida = os.path.join("../resultados", repo_name)
os.makedirs(saida, exist_ok=True)

comando = [
    "java",
    "-jar",
    "../ck/ck.jar",
    repo_path,
    "false",
    "0",
    "false",
    saida
]

print("Executando CK...")
print(" ".join(comando))

subprocess.run(comando, check=True)

print(f"Resultados salvos em: {saida}")
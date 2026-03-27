import pandas as pd

df = pd.read_csv("lab_01/Relatorios/Dados/repos_1000.csv")

# converter datas
df["createdAt"] = pd.to_datetime(df["createdAt"])
df["pushedAt"] = pd.to_datetime(df["pushedAt"])

agora = pd.Timestamp.now(tz="UTC")

# métricas
df["idade_anos"] = (agora - df["createdAt"]).dt.days / 365
df["update_days"] = (agora - df["pushedAt"]).dt.days
df["ratioClosed"] = df["closedIssuesCount"] / df["issuesTotal"]

print("RQ1 idade mediana:", df["idade_anos"].median())
print("RQ2 PRs aceitas mediana:", df["pullRequestsAccepted"].median())
print("RQ3 releases mediana:", df["releasesCount"].median())
print("RQ4 dias desde update:", df["update_days"].median())
print("RQ5 linguagens:")
print(df["primaryLanguage"].value_counts().head(10))
print("RQ6 ratio issues fechadas:", df["ratioClosed"].median())

rq7 = df.groupby("primaryLanguage").agg({
    "pullRequestsAccepted": "median",
    "releasesCount": "median",
    "update_days": "median"
}).sort_values("pullRequestsAccepted", ascending=False)

print("\nRQ7 comparação por linguagem:\n")
print(rq7.head(10))

rq7.head(10).to_csv("lab_01/Relatorios/rq7_linguagens.csv")
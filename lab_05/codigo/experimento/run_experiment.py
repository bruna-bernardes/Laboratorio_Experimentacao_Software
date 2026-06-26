import requests
import json
import time
import csv
import os
import sys
import subprocess
import signal
import statistics
from datetime import datetime

BASE_URL = "http://localhost:8000"
GRAPHQL_URL = f"{BASE_URL}/graphql"
N_REPETITIONS = 100
WARMUP_REQUESTS = 10

QUERIES = {
    "simples_rest": {
        "method": "GET",
        "url": f"{BASE_URL}/api/countries/1",
        "label": "Simples - Buscar pais por ID",
        "api": "REST",
        "complexity": "simples",
    },
    "simples_graphql": {
        "method": "POST",
        "url": GRAPHQL_URL,
        "payload": {"query": "{ country(countryId: 1) { id name region population capital } }"},
        "label": "Simples - Buscar pais por ID",
        "api": "GraphQL",
        "complexity": "simples",
    },
    "media_rest": {
        "method": "GET",
        "url": f"{BASE_URL}/api/countries?region=Europe&limit=50",
        "label": "Media - Buscar paises por regiao",
        "api": "REST",
        "complexity": "media",
    },
    "media_graphql": {
        "method": "POST",
        "url": GRAPHQL_URL,
        "payload": {"query": "{ countries(region: \"Europe\", limit: 50) { id name region population area capital } }"},
        "label": "Media - Buscar paises por regiao",
        "api": "GraphQL",
        "complexity": "media",
    },
    "complexa_rest": {
        "method": "GET",
        "url": f"{BASE_URL}/api/countries/1/details",
        "label": "Complexa - Pais com cidades, linguas e universidades",
        "api": "REST",
        "complexity": "complexa",
    },
    "complexa_graphql": {
        "method": "POST",
        "url": GRAPHQL_URL,
        "payload": {"query": "{ countryDetail(countryId: 1) { id name region population area gdp capital cities { id name population area isCapital } languages { id isOfficial percentage language { id name family speakers } } universities { id name foundedYear studentsCount ranking type } } }"},
        "label": "Complexa - Pais com cidades, linguas e universidades",
        "api": "GraphQL",
        "complexity": "complexa",
    },
}

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "dados", "raw")
RESULTS_CSV = os.path.join(RESULTS_DIR, "resultados.csv")


def start_server():
    server_path = os.path.join(PROJECT_ROOT, "codigo", "api", "server.py")
    proc = subprocess.Popen(
        [sys.executable, server_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(f"Servidor iniciado (PID={proc.pid})...")
    time.sleep(3)

    for attempt in range(30):
        try:
            r = requests.get(f"{BASE_URL}/api/countries?limit=1", timeout=2)
            if r.status_code == 200:
                print("Servidor pronto!")
                return proc
        except requests.ConnectionError:
            pass
        time.sleep(1)
    raise RuntimeError("Servidor nao respondeu apos 30 segundos")


def stop_server(proc):
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Servidor encerrado.")


def measure_request(query_def):
    if query_def["method"] == "GET":
        start = time.perf_counter()
        resp = requests.get(query_def["url"], timeout=30)
        elapsed = (time.perf_counter() - start) * 1000
        size = len(resp.content)
        status = resp.status_code
    else:
        start = time.perf_counter()
        resp = requests.post(query_def["url"], json=query_def["payload"], timeout=30)
        elapsed = (time.perf_counter() - start) * 1000
        size = len(resp.content)
        status = resp.status_code

    if status != 200:
        try:
            err = resp.json()
        except Exception:
            err = resp.text[:200]
        print(f"  ERRO: status={status}, resposta={err}")

    return elapsed, size, status


def warmup():
    print("Executando warmup...")
    for qname, qdef in QUERIES.items():
        for _ in range(WARMUP_REQUESTS):
            try:
                measure_request(qdef)
            except Exception as e:
                print(f"  Warmup erro em {qname}: {e}")
    print("Warmup concluido.")


def run_experiment():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    fieldnames = [
        "timestamp", "query_name", "label", "api", "complexity",
        "repetition", "response_time_ms", "response_size_bytes", "status_code"
    ]

    rows = []

    print(f"\nIniciando experimento: {N_REPETITIONS} repeticoes por consulta")
    print(f"Total de medicoes: {len(QUERIES) * N_REPETITIONS}")
    print("=" * 60)

    for qname, qdef in QUERIES.items():
        print(f"\nExecutando: {qname} ({qdef['label']}) [{qdef['api']}]")
        for i in range(1, N_REPETITIONS + 1):
            try:
                elapsed, size, status = measure_request(qdef)
                rows.append({
                    "timestamp": datetime.now().isoformat(),
                    "query_name": qname,
                    "label": qdef["label"],
                    "api": qdef["api"],
                    "complexity": qdef["complexity"],
                    "repetition": i,
                    "response_time_ms": round(elapsed, 3),
                    "response_size_bytes": size,
                    "status_code": status,
                })
                if i % 20 == 0:
                    print(f"  {i}/{N_REPETITIONS} - tempo: {elapsed:.2f}ms, tamanho: {size} bytes")
            except Exception as e:
                print(f"  ERRO na repeticao {i} de {qname}: {e}")
                rows.append({
                    "timestamp": datetime.now().isoformat(),
                    "query_name": qname,
                    "label": qdef["label"],
                    "api": qdef["api"],
                    "complexity": qdef["complexity"],
                    "repetition": i,
                    "response_time_ms": -1,
                    "response_size_bytes": -1,
                    "status_code": -1,
                })

    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResultados salvos em: {RESULTS_CSV}")
    print(f"Total de medicoes: {len(rows)}")

    print("\n" + "=" * 60)
    print("RESUMO POR CONSULTA")
    print("=" * 60)
    for qname, qdef in QUERIES.items():
        qrows = [r for r in rows if r["query_name"] == qname and r["response_time_ms"] > 0]
        if qrows:
            times = [r["response_time_ms"] for r in qrows]
            sizes = [r["response_size_bytes"] for r in qrows]
            print(f"\n{qname} ({qdef['api']}):")
            print(f"  Tempo  - mediana: {statistics.median(times):.2f}ms, media: {statistics.mean(times):.2f}ms, desvio: {statistics.stdev(times):.2f}ms")
            print(f"  Tamanho - mediana: {statistics.median(sizes):.0f} bytes, media: {statistics.mean(sizes):.0f} bytes")


if __name__ == "__main__":
    server_proc = None
    try:
        server_proc = start_server()
        warmup()
        run_experiment()
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        stop_server(server_proc)
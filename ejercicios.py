import requests

BASE_URL = "http://127.0.0.1:8000"

# Definición del alfabeto y lenguajes
# lambda (λ) se representa como cadena vacía ""
L = ["", "a", "b"]
M = ["b", "aa"]

print("=== 1. OPERACIONES DE CONJUNTOS ===")
print("L ∪ M:", requests.post(f"{BASE_URL}/lenguajes/union", json={"L": L, "M": M}).json()["resultado"])
print("L ∩ M:", requests.post(f"{BASE_URL}/lenguajes/interseccion", json={"L": L, "M": M}).json()["resultado"])
print("L - M:", requests.post(f"{BASE_URL}/lenguajes/diferencia", json={"L": L, "M": M}).json()["resultado"])
print("M - L:", requests.post(f"{BASE_URL}/lenguajes/diferencia", json={"L": M, "M": L}).json()["resultado"])

print("\n=== 2. OPERACIONES SOBRE CADENAS (LENGUAJES) ===")
LM = requests.post(f"{BASE_URL}/lenguajes/concatenacion", json={"L": L, "M": M}).json()["resultado"]
print("L · M:", LM)
print("M · L:", requests.post(f"{BASE_URL}/lenguajes/concatenacion", json={"L": M, "M": L}).json()["resultado"])
print("M²:", requests.post(f"{BASE_URL}/lenguajes/potencia", json={"L": M, "k": 2}).json()["resultado"])

print("\n=== 3. CLAUSURA DE KLEENE Y COMBINACIÓN ===")
print("L* (primeros 8):", requests.post(f"{BASE_URL}/lenguajes/kleene", json={"L": L, "max_len": 3}).json()["resultado"][:8])
print("M* (primeros 8):", requests.post(f"{BASE_URL}/lenguajes/kleene", json={"L": M, "max_len": 4}).json()["resultado"][:8])

# Combinación: (L · M) ∪ (M* ∩ L²)
L2 = requests.post(f"{BASE_URL}/lenguajes/potencia", json={"L": L, "k": 2}).json()["resultado"]
M_kleene_ext = requests.post(f"{BASE_URL}/lenguajes/kleene", json={"L": M, "max_len": 4}).json()["resultado"]
M_inter_L2 = requests.post(f"{BASE_URL}/lenguajes/interseccion", json={"L": M_kleene_ext, "M": L2}).json()["resultado"]
comb_final = requests.post(f"{BASE_URL}/lenguajes/union", json={"L": LM, "M": M_inter_L2}).json()["resultado"]

print("(L·M) ∪ (M* ∩ L²):", comb_final)
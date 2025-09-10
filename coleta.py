from dotenv import load_dotenv
import requests
import csv
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def coletar_repositorios():
    url_base = "https://api.github.com/search/repositories"
    repositorios = []

    for page in range(1, 11):  # 1000 repositórios = 10 páginas * 100
        print(f"🔎 Coletando página {page}...")
        params = {
            "q": "language:Java",
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page
        }
        response = requests.get(url_base, headers=HEADERS, params=params)
        data = response.json()

        for repo in data["items"]:
            repositorios.append([
                repo["name"],
                repo["full_name"],
                repo["html_url"],
                repo["stargazers_count"],
                repo["created_at"],
                repo["pushed_at"]
            ])

    # Salvar em CSV
    with open("repositorios.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "full_name", "url", "stars", "created_at", "last_push"])
        writer.writerows(repositorios)

    print("✅ Lista salva em repositorios.csv")

if __name__ == "__main__":
    coletar_repositorios()

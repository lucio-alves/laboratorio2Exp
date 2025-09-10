import os
import subprocess
from typing import List

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
REPOS_DIR = os.path.join(BASE_DIR, "repos")
os.makedirs(REPOS_DIR, exist_ok=True)

# Coloque aqui a sua lista (ou leia de um arquivo)
REPOS: List[str] = [
    "https://github.com/krahets/hello-algo",
    
]

def folder_name_from_url(url: str) -> str:
    owner, repo = url.rstrip("/").split("/")[-2:]
    return f"{owner}__{repo}"

def run(cmd: list, cwd: str = None):
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=cwd)

def clone_or_update(url: str):
    name = folder_name_from_url(url)
    dest = os.path.join(REPOS_DIR, name)
    if not os.path.exists(dest):
        print(f"📥 Clonando {url} em {dest} ...")
        run(["git", "clone", "--depth", "1", url, dest])
    else:
        print(f"📂 {name} já existe. Atualizando...")
        run(["git", "-C", dest, "fetch", "--tags", "--prune"])
        run(["git", "-C", dest, "pull", "--ff-only"])

if __name__ == "__main__":
    for url in REPOS:
        try:
            clone_or_update(url)
        except subprocess.CalledProcessError as e:
            print(f"❌ Falha ao processar {url}: {e}")

import os
import subprocess
import pandas as pd
import sys

CK_JAR = "ckjm-1.9.jar"
RESULTADOS_DIR = "resultados"
REPO_URL = "https://github.com/redisson/redisson"
REPO_DIR = "repo_teste"

def clonar_repositorio(url, destino=REPO_DIR):
    if not os.path.exists(destino):
        print(f"📥 Clonando {url}...")
        subprocess.run(["git", "clone", "--depth", "1", url, destino])
    else:
        print("📂 Repositório já clonado.")

def compilar_repositorio(diretorio_repo):
    os.chdir(diretorio_repo)

    if os.path.exists("pom.xml"):
        print("⚙️ Projeto Maven detectado. Compilando...")
        result = subprocess.run(["mvn", "clean", "compile"], capture_output=True, text=True)
    elif os.path.exists("gradlew") or os.path.exists("gradlew.bat"):
        wrapper = "gradlew.bat" if os.path.exists("gradlew.bat") else "gradlew"
        print(f"⚙️ Projeto Gradle detectado. Usando wrapper {wrapper}...")
        result = subprocess.run([os.path.join(os.getcwd(), wrapper), "build"], capture_output=True, text=True, shell=True)
    elif os.path.exists("build.gradle"):
        print("⚙️ Projeto Gradle detectado. Compilando (Gradle deve estar instalado)...")
        result = subprocess.run(["gradle", "build"], capture_output=True, text=True)
    else:
        print("❌ Nenhum build system encontrado (Maven/Gradle). Abortando CK.")
        sys.exit(1)

    if result.returncode != 0:
        print("❌ Erro ao compilar o projeto:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

    os.chdir("..")

def encontrar_pasta_classes(diretorio_repo):
    # Maven padrão
    maven_path = os.path.join(diretorio_repo, "target", "classes")
    if os.path.exists(maven_path):
        return maven_path
    # Gradle padrão
    gradle_path = os.path.join(diretorio_repo, "build", "classes", "java", "main")
    if os.path.exists(gradle_path):
        return gradle_path
    print("❌ Pasta de classes compiladas não encontrada.")
    sys.exit(1)

def rodar_ck(classes_dir):
    os.makedirs(RESULTADOS_DIR, exist_ok=True)
    comando = [
        "java", "-jar", CK_JAR, classes_dir, "true", "0", "false", RESULTADOS_DIR
    ]
    print("⚙️ Rodando CK...")
    subprocess.run(comando)

def ler_resultado():
    csv_path = os.path.join(RESULTADOS_DIR, "class.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print("📊 Métricas coletadas (primeiras linhas):")
        print(df.head())
    else:
        print("❌ Arquivo de métricas não encontrado!")

if __name__ == "__main__":
    clonar_repositorio(REPO_URL)
    compilar_repositorio(REPO_DIR)
    classes_dir = encontrar_pasta_classes(REPO_DIR)
    rodar_ck(classes_dir)
    ler_resultado()

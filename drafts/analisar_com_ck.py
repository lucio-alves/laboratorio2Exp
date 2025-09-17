import os
import glob
import subprocess
import pandas as pd

# 🔹 Caminho absoluto para o jar “-jar-with-dependencies”
CK_JAR = r"C:\Users\kingl\Desktop\ck-ck-0.7.0\ck-ck-0.7.0\target\ck-0.7.0-jar-with-dependencies.jar"

# 🔹 Forçando o Java correto (JDK 21)
JAVA_BIN = r"C:\Program Files\Eclipse Adoptium\jdk-21.0.8.9-hotspot\bin\java.exe"
print("Usando java em:", JAVA_BIN)

# 🔹 Diretório onde serão salvos os resultados
RESULTADOS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resultados")
os.makedirs(RESULTADOS_DIR, exist_ok=True)

IGNORAR_DIRS = [
    "target/", "build/", "out/", ".git/", ".github/", ".idea/", 
    "node_modules/", "generated-sources/", "src/test/"
]

# 🔹 Coloque aqui o caminho do repositório até a pasta que contém os arquivos .java
REPO_DIR = r"C:\Users\kingl\Desktop\puc minas 1\repos\krahets__hello-algo\codes\java"

def tem_java_sources(repo_dir: str) -> bool:
    return any(glob.iglob(os.path.join(repo_dir, "**", "*.java"), recursive=True))

def run(cmd: list, cwd: str = None):
    print(">", " ".join(str(c) for c in cmd))
    result = subprocess.run(cmd, text=True, capture_output=True, cwd=cwd)
    if result.returncode != 0:
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result

def nome_repo(path: str) -> str:
    return os.path.basename(path.rstrip(os.sep))

def rodar_ck_no_repo(repo_dir: str):
    if not tem_java_sources(repo_dir):
        print(f"⚠️ Sem arquivos .java em {repo_dir}. Pulando.")
        return

    out_dir = os.path.join(RESULTADOS_DIR, nome_repo(repo_dir))
    os.makedirs(out_dir, exist_ok=True)

    cmd = [JAVA_BIN, "-jar", CK_JAR, repo_dir, "true", "0", "false", out_dir] + IGNORAR_DIRS
    print(f"⚙️ Rodando CK em {repo_dir} -> {out_dir}")
    run(cmd)

    esperados = ["javaclass.csv", "javamethod.csv", "javavariable.csv"]  

    gerados = [f for f in esperados if os.path.exists(os.path.join(out_dir, f))]
    if gerados:
        print(f"✅ Gerados: {', '.join(gerados)}")
    else:
        print("❌ Nenhum CSV encontrado. Verifique o jar/paths e stderr acima.")

def agregar_classes_csv():
    frames = []
    for repo_out in glob.glob(os.path.join(RESULTADOS_DIR, "*")):
        csv_path = os.path.join(repo_out, "class.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.insert(0, "repo", os.path.basename(repo_out))
            frames.append(df)
    if frames:
        big = pd.concat(frames, ignore_index=True)
        out_csv = os.path.join(RESULTADOS_DIR, "class__ALL.csv")
        big.to_csv(out_csv, index=False)
        print(f"📊 Agregado salvo em: {out_csv}")
    else:
        print("⚠️ Nenhum class.csv encontrado para agregar.")

if __name__ == "__main__":
    if not os.path.isfile(CK_JAR):
        raise SystemExit(f"Jar do CK não encontrado:\n{CK_JAR}")

    falhas = []
    try:
        rodar_ck_no_repo(REPO_DIR)
    except subprocess.CalledProcessError as e:
        falhas.append((REPO_DIR, e.returncode))
        print(f"❌ Falha no CK para {REPO_DIR}: code={e.returncode}")

    print("\n=== Agregando CSVs de classes (opcional) ===")
    agregar_classes_csv()

    if falhas:
        print("\nRepos com falha:")
        for r, code in falhas:
            print("-", r, "(exit code:", code, ")")

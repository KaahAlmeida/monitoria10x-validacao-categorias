import streamlit as st
import pandas as pd
import random

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Monitoria 10x | Validação de Categorias",
    layout="wide"
)

st.title("🎧 Monitoria 10x – Validação de Categorias")
st.caption("Simulador didático de Speech Analytics")

st.divider()

# =========================
# BASE DE TRANSCRIÇÕES
# =========================
def gerar_transcricoes():
    dados = [
        ("CLIENTE", "quero cancelar o contrato porque o atendimento foi péssimo", "Cancelamento"),
        ("CLIENTE", "não recebi minha fatura esse mês", "Fatura"),
        ("CLIENTE", "estou ligando apenas para tirar uma dúvida", "Duvida"),
        ("CLIENTE", "não quero cancelar, só entender o valor", "Cancelamento"),
        ("CLIENTE", "vou cancelar se isso não for resolvido", "Cancelamento"),
        ("CLIENTE", "o atendimento demorou muito", "Reclamacao"),
        ("AGENTE", "vou verificar sua solicitação no sistema", "Atendimento"),
        ("AGENTE", "posso ajudar em algo mais?", "Atendimento"),
    ]
    random.shuffle(dados)
    return pd.DataFrame(dados, columns=["Lado", "Transcrição", "Categoria Esperada"])

df = gerar_transcricoes()
st.dataframe(df, use_container_width=True)

st.divider()

# =========================
# CONFIGURAÇÃO DAS CATEGORIAS
# =========================
st.header("📌 Criação de Categorias")

categorias = []

for i in range(1, 4):
    with st.expander(f"Categoria {i}"):
        nome = st.text_input("Nome da categoria", key=f"nome_{i}")
        lado = st.selectbox("Analisar lado", ["CLIENTE", "AGENTE", "AMBOS"], key=f"lado_{i}")

        termos = []
        for t in range(1, 3):
            termo = st.text_input(f"Termo {t} (pode ter mais de uma palavra)", key=f"termo_{i}_{t}")
            slop = st.slider(f"Slop do termo {t}", 0, 6, 2, key=f"slop_{i}_{t}")
            if termo:
                termos.append({"texto": termo.lower(), "slop": slop})

        if nome and termos:
            categorias.append({
                "nome": nome,
                "lado": lado,
                "termos": termos
            })

st.divider()

# =========================
# FUNÇÕES DE VALIDAÇÃO (CORRETAS)
# =========================
def termo_aciona(texto, termo, slop):
    tokens = texto.lower().split()
    palavras = termo.split()

    indices = []
    for p in palavras:
        pos = [i for i, tok in enumerate(tokens) if tok == p]
        if not pos:
            return False
        indices.append(pos[0])

    distancia = max(indices) - min(indices)
    return distancia <= slop


def categoria_aciona(texto, termos):
    for t in termos:
        if not termo_aciona(texto, t["texto"], t["slop"]):
            return False
    return True

# =========================
# EXECUÇÃO
# =========================
st.header("📊 Resultado")

if st.button("Validar Categorias"):
    resultados = []

    for cat in categorias:
        acertos = 0
        total = 0

        for _, row in df.iterrows():
            if cat["lado"] != "AMBOS" and row["Lado"] != cat["lado"]:
                continue

            acionou = categoria_aciona(row["Transcrição"], cat["termos"])
            total += 1

            if acionou and row["Categoria Esperada"] == cat["nome"]:
                acertos += 1

            resultados.append({
                "Categoria": cat["nome"],
                "Transcrição": row["Transcrição"],
                "Acionou": "Sim" if acionou else "Não"
            })

        taxa = round((acertos / total) * 100, 2) if total else 0
        st.metric(f"🎯 {cat['nome']}", f"{taxa}%")

    st.divider()
    st.dataframe(pd.DataFrame(resultados), use_container_width=True)

st.caption("Simulador didático — lógica equivalente a Speech Analytics real.")














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

# =========================
# CABEÇALHO
# =========================
st.markdown("""
<div style="text-align:center; background-color:#4B8BBE; padding:15px; border-radius:10px">
    <h1 style="color:white;">🎧 Monitoria 10x – Validação de Categorias</h1>
    <p style="color:white; font-size:16px;">Simulador didático de Speech Analytics</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:10px; margin-bottom:10px;">
Treine a validação de categorias de forma clara e didática.  
Crie **mais de uma categoria**, cada uma com **até 2 termos**, cada termo com **slop individual**.
</div>
""", unsafe_allow_html=True)

st.divider()

# =========================
# BASES DE TRANSCRIÇÕES
# =========================
st.header("1️⃣ Base de Transcrições")

st.info("Esta base simula ligações reais. O campo **Categoria Esperada** indica qual categoria deveria acionar.")

def gerar_transcricoes(base=1):
    if base == 1:
        dados = [
            ("CLIENTE", "quero cancelar o contrato porque o atendimento foi péssimo", "Cancelamento"),
            ("CLIENTE", "não recebi minha fatura esse mês", "Fatura"),
            ("CLIENTE", "estou ligando apenas para tirar uma dúvida", "Duvida"),
            ("CLIENTE", "não quero cancelar, só entender o valor", "Cancelamento"),
            ("CLIENTE", "vou cancelar se isso não for resolvido", "Cancelamento"),
            ("CLIENTE", "o atendimento demorou muito", "Reclamacao"),
            ("AGENTE", "vou verificar sua solicitação no sistema", "Atendimento"),
            ("AGENTE", "posso ajudar em algo mais?", "Atendimento"),
            ("AGENTE", "vou encaminhar para o setor responsável", "Atendimento"),
        ]
    else:
        dados = [
            ("CLIENTE", "gostaria de encerrar meu plano imediatamente", "Cancelamento"),
            ("CLIENTE", "como posso alterar minha assinatura?", "Duvida"),
            ("CLIENTE", "não recebi minha fatura de janeiro", "Fatura"),
            ("CLIENTE", "apenas quero esclarecer algumas dúvidas", "Duvida"),
            ("CLIENTE", "cancelamento urgente, por favor", "Cancelamento"),
            ("AGENTE", "vou abrir um chamado para você", "Atendimento"),
            ("AGENTE", "preciso que envie seus documentos", "Atendimento"),
        ]
    random.shuffle(dados)
    return pd.DataFrame(dados, columns=["Lado", "Transcrição", "Categoria Esperada"])

base_selecionada = st.selectbox("Escolha a base de transcrições", ["Base 1", "Base 2"])
df = gerar_transcricoes(base=1 if base_selecionada=="Base 1" else 2)
st.dataframe(df, use_container_width=True)

st.divider()

# =========================
# CONFIGURAÇÃO DE CATEGORIAS
# =========================
st.header("2️⃣ Crie suas Categorias")

st.markdown("""
Cada categoria pode ter **até 2 termos**, e cada termo pode ter seu **slop individual** (distância máxima entre palavras).  
A categoria aciona apenas se **todos os termos acionarem dentro do seu slop**.
""")

categorias = []
for i in range(1, 4):
    with st.expander(f"Categoria {i}"):
        nome = st.text_input(f"Nome da Categoria {i}", key=f"nome_{i}")
        termos = []
        for t in range(1, 3):  # máximo 2 termos
            termo = st.text_input(f"Termo {t}", key=f"c{i}_t{t}")
            slop = st.slider(f"Slop do termo {t}", 0, 5, 2, key=f"c{i}_s{t}")
            if termo:
                termos.append({"palavra": termo, "slop": slop})
        lado = st.selectbox(f"Analisar lado da Categoria {i}", ["CLIENTE", "AGENTE", "AMBOS"], key=f"c{i}_lado")
        if nome and termos:
            categorias.append({"nome": nome, "termos": termos, "lado": lado})

st.divider()

# =========================
# FUNÇÃO DE VALIDAÇÃO COM SLOP REAL
# =========================
def valida_categoria(texto, termos):
    """
    Valida categoria com até 2 termos e slop individual.
    """
    tokens = texto.lower().split()
    if len(termos) == 1:
        # 1 termo: aciona se palavra existir
        return termos[0]["palavra"].lower() in tokens

    # 2 termos
    palavra1 = termos[0]["palavra"].lower()
    palavra2 = termos[1]["palavra"].lower()
    slop1 = termos[0]["slop"]
    slop2 = termos[1]["slop"]

    # encontra todos os índices da primeira palavra
    indices1 = [i for i, t in enumerate(tokens) if t == palavra1]
    if not indices1:
        return False

    # encontra todos os índices da segunda palavra
    indices2 = [i for i, t in enumerate(tokens) if t == palavra2]
    if not indices2:
        return False

    # verifica se existe algum par de posições que respeita o slop individual
    for i1 in indices1:
        for i2 in indices2:
            distancia = abs(i1 - i2)
            if distancia <= max(slop1, slop2):
                return True
    return False

# =========================
# EXECUÇÃO DA VALIDAÇÃO
# =========================
st.header("3️⃣ Resultados")

if st.button("🔍 Validar Categorias"):

    if not categorias:
        st.warning("Crie pelo menos uma categoria com pelo menos 1 termo.")
    else:
        resultados = []
        metrics = []

        for cat in categorias:
            vp = 0
            total = 0
            for _, row in df.iterrows():
                if cat["lado"] != "AMBOS" and row["Lado"] != cat["lado"]:
                    continue
                acionou = valida_categoria(row["Transcrição"], cat["termos"])
                total += 1
                if row["Categoria Esperada"] == cat["nome"] and acionou:
                    vp += 1
                resultados.append({
                    "Categoria": cat["nome"],
                    "Transcrição": row["Transcrição"],
                    "Acionou": "Sim" if acionou else "Não"
                })
            taxa = round((vp / total) * 100, 2) if total else 0
            metrics.append({"Categoria": cat["nome"], "Taxa de Acerto": taxa})

        # =========================
        # DASHBOARD DE MÉTRICAS
        # =========================
        st.markdown("### 📊 Taxa de Acerto por Categoria")
        col_count = len(metrics)
        cols = st.columns(col_count)
        for idx, m in enumerate(metrics):
            cols[idx].markdown(f'<div style="background-color:#F9E79F; padding:15px; border-radius:10px; text-align:center">'
                               f'<h3>{m["Categoria"]}</h3><h2>{m["Taxa de Acerto"]}%</h2></div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📝 Resultados Detalhados")
        st.dataframe(pd.DataFrame(resultados), use_container_width=True)

        st.markdown("💡 Ajuste os termos e slop de cada termo para melhorar a taxa de acerto!")

st.divider()
st.caption("""
📌 Este simulador é didático. Dados simulados e lógica simplificada para aprendizado.
""")












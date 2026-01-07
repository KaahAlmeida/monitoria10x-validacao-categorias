import streamlit as st
import pandas as pd
import re

# =========================================================
# CONFIGURAÇÃO DA PÁGINA (SEMPRE PRIMEIRA LINHA)
# =========================================================
st.set_page_config(
    page_title="Monitoria 10x – Validação de Categorias",
    layout="wide"
)

# =========================================================
# FUNÇÕES DE MATCH (COM SLOP REAL)
# =========================================================
def normalizar(texto):
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto.split()

def termo_bate(transcricao, termo, slop):
    trans_tokens = normalizar(transcricao)
    termo_tokens = normalizar(termo)

    if not termo_tokens:
        return False

    if len(termo_tokens) == 1:
        return termo_tokens[0] in trans_tokens

    for i in range(len(trans_tokens)):
        if trans_tokens[i] == termo_tokens[0]:
            idx = i
            encontrou = True
            for t in termo_tokens[1:]:
                proximos = trans_tokens[idx + 1: idx + slop + 2]
                if t in proximos:
                    idx = idx + 1 + proximos.index(t)
                else:
                    encontrou = False
                    break
            if encontrou:
                return True
    return False

def categoria_bate(transcricao, termos):
    for termo in termos:
        if termo_bate(transcricao, termo["texto"], termo["slop"]):
            return True
    return False

# =========================================================
# CABEÇALHO VISUAL
# =========================================================
st.markdown(
    """
    <div style="padding:20px 0;">
        <h1 style="margin-bottom:0;">🎧 Monitoria 10x – Validação de Categorias</h1>
        <p style="color:gray; margin-top:5px;">
            Simulador didático de Speech Analytics
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================================================
# BASE DE TRANSCRIÇÕES
# =========================================================
st.subheader("📄 Base de Transcrições")

base = pd.DataFrame({
    "Lado": [
        "CLIENTE", "CLIENTE", "CLIENTE", "CLIENTE",
        "AGENTE", "CLIENTE", "AGENTE", "CLIENTE"
    ],
    "Transcrição": [
        "quero cancelar o contrato porque o atendimento foi péssimo",
        "não recebi minha fatura esse mês",
        "estou ligando apenas para tirar uma dúvida",
        "não quero cancelar, só entender o valor",
        "vou verificar sua solicitação no sistema",
        "vou cancelar se isso não for resolvido",
        "posso ajudar em algo mais",
        "o atendimento demorou muito"
    ],
    "Categoria Esperada": [
        "Cancelamento", "Fatura", "Duvida", "Cancelamento",
        "Atendimento", "Cancelamento", "Atendimento", "Reclamacao"
    ]
})

st.dataframe(base, use_container_width=True)

# =========================================================
# ESCOLHA DA TRANSCRIÇÃO
# =========================================================
st.subheader("🎯 Escolha uma transcrição para validação")

linha = st.selectbox(
    "Selecione o índice da transcrição:",
    base.index
)

transcricao = base.loc[linha, "Transcrição"]
categoria_esperada = base.loc[linha, "Categoria Esperada"]

st.info(f"📝 **Transcrição selecionada:** {transcricao}")
st.info(f"🎯 **Categoria esperada:** {categoria_esperada}")

# =========================================================
# CRIAÇÃO DE CATEGORIAS
# =========================================================
st.subheader("🧠 Construção das Categorias")

qtd = st.number_input(
    "Quantas categorias você deseja criar?",
    min_value=1,
    max_value=5,
    value=1
)

categorias = []

for i in range(qtd):
    st.markdown(f"### Categoria {i+1}")
    nome = st.text_input(f"Nome da categoria", key=f"nome_{i}")

    termos = []

    for t in range(2):
        col1, col2 = st.columns([3, 1])
        with col1:
            termo = st.text_input(
                f"Termo {t+1}",
                key=f"termo_{i}_{t}"
            )
        with col2:
            slop = st.number_input(
                "Slop",
                min_value=0,
                max_value=5,
                value=2,
                key=f"slop_{i}_{t}"
            )

        if termo.strip():
            termos.append({"texto": termo, "slop": slop})

    if nome.strip() and termos:
        categorias.append({
            "nome": nome,
            "termos": termos
        })

# =========================================================
# VALIDAÇÃO
# =========================================================
st.divider()
st.subheader("📊 Resultado")

if st.button("Validar Categorias"):
    detectadas = []

    for cat in categorias:
        if categoria_bate(transcricao, cat["termos"]):
            detectadas.append(cat["nome"])

    if detectadas:
        st.success(f"Categorias detectadas: {', '.join(detectadas)}")
    else:
        st.warning("Nenhuma categoria foi detectada.")

    if categoria_esperada in detectadas:
        st.success("✅ Categoria correta identificada!")
    else:
        st.error("❌ Categoria correta NÃO foi identificada.")

# =========================================================
# RODAPÉ
# =========================================================
st.divider()
st.caption("Monitoria 10x • Simulador educacional")

















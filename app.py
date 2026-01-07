import streamlit as st
import pandas as pd
import re

# =========================================================
# CONFIGURAÇÃO DA PÁGINA (OBRIGATORIAMENTE PRIMEIRO)
# =========================================================
st.set_page_config(
    page_title="Monitoria 10x – Validação de Categorias",
    layout="wide"
)

# =========================================================
# FUNÇÕES DE MATCH (LÓGICA CORRETA COM SLOP REAL)
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

    # termo com uma palavra
    if len(termo_tokens) == 1:
        return termo_tokens[0] in trans_tokens

    # termo com mais de uma palavra (com slop)
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
# CABEÇALHO
# =========================================================
st.title("🎧 Monitoria 10x – Validação de Categorias")
st.caption("Simulador didático de Speech Analytics")

st.divider()

# =========================================================
# BASE FIXA DE TRANSCRIÇÕES (COM OPÇÃO DE TROCAR)
# =========================================================
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

st.subheader("📄 Base de Transcrições")
st.dataframe(base, use_container_width=True)

# =========================================================
# ESCOLHA DA TRANSCRIÇÃO PARA TESTE
# =========================================================
st.subheader("🎯 Escolha uma transcrição para validar")

linha = st.selectbox(
    "Selecione o índice da transcrição:",
    base.index
)

transcricao_selecionada = base.loc[linha, "Transcrição"]
categoria_esperada = base.loc[linha, "Categoria Esperada"]

st.info(f"**Transcrição selecionada:** {transcricao_selecionada}")
st.info(f"**Categoria esperada:** {categoria_esperada}")

# =========================================================
# CRIAÇÃO DAS CATEGORIAS PELO ALUNO
# =========================================================
st.subheader("🧠 Criação de Categorias")

qtd_categorias = st.number_input(
    "Quantas categorias deseja criar?",
    min_value=1,
    max_value=5,
    value=1
)

categorias = []

for i in range(qtd_categorias):
    st.markdown(f"### Categoria {i+1}")
    nome = st.text_input(f"Nome da categoria {i+1}", key=f"cat_nome_{i}")

    termos = []

    for t in range(2):  # NO MÁXIMO 2 TERMOS
        col1, col2 = st.columns([3, 1])
        with col1:
            texto_termo = st.text_input(
                f"Termo {t+1} da categoria {i+1}",
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

        if texto_termo.strip():
            termos.append({
                "texto": texto_termo,
                "slop": slop
            })

    if nome.strip() and termos:
        categorias.append({
            "nome": nome,
            "termos": termos
        })

# =========================================================
# AVALIAÇÃO
# =========================================================
st.divider()
st.subheader("📊 Resultado da Validação")

if st.button("Validar Categorias"):
    categorias_detectadas = []

    for cat in categorias:
        if categoria_bate(transcricao_selecionada, cat["termos"]):
            categorias_detectadas.append(cat["nome"])

    if categorias_detectadas:
        st.success(f"Categorias detectadas: {', '.join(categorias_detectadas)}")
    else:
        st.warning("Nenhuma categoria foi detectada.")

    # Pontuação simples e clara (didática)
    if categoria_esperada in categorias_detectadas:
        st.success("✅ Parabéns! A categoria correta foi identificada.")
    else:
        st.error("❌ A categoria correta não foi identificada.")

# =========================================================
# RODAPÉ
# =========================================================
st.divider()
st.caption("Simulador educacional • Monitoria 10x")















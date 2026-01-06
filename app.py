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

st.markdown("""
Esta página foi criada para **treinar validação de categorias**, mesmo sem acesso à ferramenta oficial.

👉 Aqui você vai:
- Criar uma categoria
- Testar em transcrições simuladas
- Identificar falsos positivos e negativos
- Avaliar a **taxa de acerto**
""")

st.divider()

# =========================
# GERADOR DE TRANSCRIÇÕES
# =========================
st.header("1️⃣ Base de Transcrições")

st.info(
    "Para fins didáticos, esta base simula ligações reais. "
    "O campo **Esperado** indica se a categoria *deveria* acionar ou não."
)

def gerar_transcricoes():
    dados = [
        ("CLIENTE", "quero cancelar o contrato porque o atendimento foi péssimo", True),
        ("CLIENTE", "não recebi minha fatura esse mês", True),
        ("CLIENTE", "estou ligando apenas para tirar uma dúvida", False),
        ("CLIENTE", "não quero cancelar, só entender o valor", False),
        ("CLIENTE", "vou cancelar se isso não for resolvido", True),
        ("CLIENTE", "o atendimento demorou muito", True),
        ("AGENTE", "vou verificar sua solicitação no sistema", False),
        ("AGENTE", "posso ajudar em algo mais?", False),
        ("AGENTE", "vou encaminhar para o setor responsável", False),
    ]
    random.shuffle(dados)
    return pd.DataFrame(dados, columns=["Lado", "Transcrição", "Esperado"])

df = gerar_transcricoes()
st.dataframe(df, use_container_width=True)

st.divider()

# =========================
# CONFIGURAÇÃO DA CATEGORIA
# =========================
st.header("2️⃣ Configuração da Categoria")

st.markdown("""
Agora configure sua categoria como faria na ferramenta real.
Comece simples e ajuste conforme o resultado.
""")

col1, col2, col3 = st.columns(3)

with col1:
    termos_contem = st.text_area(
        "Termos que DEVEM / PODEM conter",
        placeholder="cancelar, cancelar contrato"
    )

with col2:
    termos_nao_contem = st.text_area(
        "Termos que NÃO devem conter",
        placeholder="não quero cancelar"
    )

with col3:
    operador = st.selectbox("Operador lógico", ["OU", "E"])
    lado = st.selectbox("Analisar lado", ["CLIENTE", "AGENTE", "AMBOS"])

slop = st.slider(
    "Slop (distância máxima entre palavras)",
    min_value=0,
    max_value=10,
    value=3
)

st.caption(
    "💡 Dica: Slop ajuda a evitar falsos positivos quando usamos mais de uma palavra."
)

st.divider()

# =========================
# FUNÇÕES DE VALIDAÇÃO
# =========================
def valida_slop(texto, palavras, slop):
    tokens = texto.lower().split()
    indices = []

    for palavra in palavras:
        palavra = palavra.lower()
        if palavra in tokens:
            indices.append(tokens.index(palavra))

    if len(indices) < len(palavras):
        return False

    return max(indices) - min(indices) <= slop


def valida_categoria(texto):
    texto = texto.lower()

    termos_c = [t.strip() for t in termos_contem.split(",") if t.strip()]
    termos_nc = [t.strip() for t in termos_nao_contem.split(",") if t.strip()]

    if not termos_c:
        return False

    if operador == "OU":
        match = any(t.lower() in texto for t in termos_c)
    else:
        match = all(t.lower() in texto for t in termos_c)

    if termos_nc:
        if any(t.lower() in texto for t in termos_nc):
            return False

    if slop > 0 and len(termos_c) > 1:
        return valida_slop(texto, termos_c, slop) and match

    return match


# =========================
# EXECUÇÃO DA VALIDAÇÃO
# =========================
st.header("3️⃣ Resultado da Validação")

if st.button("🔍 Validar Categoria"):

    resultados = []

    for _, row in df.iterrows():

        if lado != "AMBOS" and row["Lado"] != lado:
            continue

        acionou = valida_categoria(row["Transcrição"])

        resultados.append({
            "Lado": row["Lado"],
            "Transcrição": row["Transcrição"],
            "Esperado": "Sim" if row["Esperado"] else "Não",
            "Categoria acionou": "Sim" if acionou else "Não"
        })

    res = pd.DataFrame(resultados)

    vp = len(res[(res["Esperado"] == "Sim") & (res["Categoria acionou"] == "Sim")])
    fp = len(res[(res["Esperado"] == "Não") & (res["Categoria acionou"] == "Sim")])
    fn = len(res[(res["Esperado"] == "Sim") & (res["Categoria acionou"] == "Não")])
    vn = len(res[(res["Esperado"] == "Não") & (res["Categoria acionou"] == "Não")])

    total = vp + fp + fn + vn
    taxa_acerto = round(((vp + vn) / total) * 100, 2) if total else 0

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("Verdadeiro Positivo", vp)
        st.metric("Falso Positivo", fp)

    with col_b:
        st.metric("Falso Negativo", fn)
        st.metric("Verdadeiro Negativo", vn)

    with col_c:
        st.metric("🎯 Taxa de Acerto (%)", taxa_acerto)

    st.divider()
    st.dataframe(res, use_container_width=True)

    # =========================
    # FEEDBACK DIDÁTICO
    # =========================
    if taxa_acerto >= 85:
        st.success(
            "Excelente! Sua categoria está bem ajustada. "
            "Agora você poderia escalar ou criar uma agregadora."
        )
    elif taxa_acerto >= 65:
        st.warning(
            "Categoria razoável. "
            "Tente reduzir falsos positivos ou melhorar os termos."
        )
    else:
        st.error(
            "Categoria mal ajustada. "
            "Revise termos, operador lógico ou slop."
        )

st.divider()

st.caption("""
📌 Importante:  
Este simulador é didático. A lógica é a mesma da ferramenta real,  
mas os dados são simulados para fins de aprendizado.
""")

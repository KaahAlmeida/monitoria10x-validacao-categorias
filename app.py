import streamlit as st
import pandas as pd
import random

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Monitoria 10x | Validação de Categorias",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CABEÇALHO BONITO
# =========================
st.markdown("""
<div style="text-align:center; background-color:#4B8BBE; padding:15px; border-radius:10px">
    <h1 style="color:white;">🎧 Monitoria 10x – Validação de Categorias</h1>
    <p style="color:white; font-size:16px;">Simulador didático de Speech Analytics</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:10px; margin-bottom:10px;">
Treine a validação de categorias de forma **didática e simples**.  
**Objetivos**:
- Criar uma categoria
- Testar em transcrições simuladas
- Avaliar a **taxa de acerto**
</div>
""", unsafe_allow_html=True)

st.divider()

# =========================
# BASE DE TRANSCRIÇÕES
# =========================
st.header("1️⃣ Base de Transcrições")

st.info(
    "Esta base simula ligações reais. "
    "O campo **Esperado** indica se a categoria *deveria* acionar ou não."
)

# Função para gerar duas bases diferentes
def gerar_transcricoes(base=1):
    if base == 1:
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
    else:
        dados = [
            ("CLIENTE", "gostaria de encerrar meu plano imediatamente", True),
            ("CLIENTE", "como posso alterar minha assinatura?", False),
            ("CLIENTE", "não recebi minha fatura de janeiro", True),
            ("CLIENTE", "apenas quero esclarecer algumas dúvidas", False),
            ("CLIENTE", "cancelamento urgente, por favor", True),
            ("AGENTE", "vou abrir um chamado para você", False),
            ("AGENTE", "preciso que envie seus documentos", False),
        ]
    random.shuffle(dados)
    return pd.DataFrame(dados, columns=["Lado", "Transcrição", "Esperado"])

# Seleção de base pelo aluno
base_selecionada = st.selectbox("Escolha a base de transcrições", ["Base 1", "Base 2"])
df = gerar_transcricoes(base=1 if base_selecionada=="Base 1" else 2)
st.dataframe(df, use_container_width=True)

st.divider()

# =========================
# CONFIGURAÇÃO DA CATEGORIA
# =========================
st.header("2️⃣ Configuração da Categoria")

st.markdown("""
Configure sua categoria de forma simples: **somente termos que DEVEM conter**.
""")

termos_contem = st.text_area(
    "Termos que DEVEM conter",
    placeholder="cancelar, cancelar contrato"
)

lado = st.selectbox("Analisar lado", ["CLIENTE", "AGENTE", "AMBOS"])

st.divider()

# =========================
# FUNÇÕES DE VALIDAÇÃO
# =========================
def valida_categoria(texto, termos):
    texto = texto.lower()
    termos_c = [t.strip() for t in termos.split(",") if t.strip()]
    if not termos_c:
        return False
    # Verifica se todos os termos obrigatórios estão presentes
    return all(t.lower() in texto for t in termos_c)

# =========================
# EXECUÇÃO DA VALIDAÇÃO
# =========================
st.header("3️⃣ Resultado da Validação")

if st.button("🔍 Validar Categoria"):
    resultados = []

    for _, row in df.iterrows():
        if lado != "AMBOS" and row["Lado"] != lado:
            continue

        acionou = valida_categoria(row["Transcrição"], termos_contem)

        resultados.append({
            "Lado": row["Lado"],
            "Transcrição": row["Transcrição"],
            "Esperado": "Sim" if row["Esperado"] else "Não",
            "Categoria acionou": "Sim" if acionou else "Não"
        })

    res = pd.DataFrame(resultados)

    # =========================
    # MÉTRICAS VISUAIS
    # =========================
    vp = len(res[(res["Esperado"] == "Sim") & (res["Categoria acionou"] == "Sim")])
    fp = len(res[(res["Esperado"] == "Não") & (res["Categoria acionou"] == "Sim")])
    fn = len(res[(res["Esperado"] == "Sim") & (res["Categoria acionou"] == "Não")])
    vn = len(res[(res["Esperado"] == "Não") & (res["Categoria acionou"] == "Não")])

    total = vp + fp + fn + vn
    taxa_acerto = round(((vp + vn) / total) * 100, 2) if total else 0

    st.markdown("### 📊 Métricas da Categoria")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(f'<div style="background-color:#D1F2EB; padding:15px; border-radius:10px; text-align:center">'
                    f'<h3>✅ Verdadeiro Positivo</h3><h2>{vp}</h2></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="background-color:#F5B7B1; padding:15px; border-radius:10px; text-align:center; margin-top:10px">'
                    f'<h3>❌ Falso Positivo</h3><h2>{fp}</h2></div>', unsafe_allow_html=True)

    with col_b:
        st.markdown(f'<div style="background-color:#F5B7B1; padding:15px; border-radius:10px; text-align:center">'
                    f'<h3>❌ Falso Negativo</h3><h2>{fn}</h2></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="background-color:#D1F2EB; padding:15px; border-radius:10px; text-align:center; margin-top:10px">'
                    f'<h3>✅ Verdadeiro Negativo</h3><h2>{vn}</h2></div>', unsafe_allow_html=True)

    with col_c:
        st.markdown(f'<div style="background-color:#F9E79F; padding:20px; border-radius:10px; text-align:center">'
                    f'<h3>🎯 Taxa de Acerto (%)</h3><h2>{taxa_acerto}</h2></div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### 📝 Resultados Detalhados")
    st.dataframe(res, use_container_width=True)

    st.markdown("### 💡 Feedback")
    if taxa_acerto >= 85:
        st.success("Excelente! Sua categoria está bem ajustada.")
    elif taxa_acerto >= 65:
        st.warning("Categoria razoável. Tente melhorar os termos.")
    else:
        st.error("Categoria mal ajustada. Revise os termos ou a base de transcrições.")

st.divider()
st.caption("""
📌 Importante:  
Este simulador é didático. A lógica é a mesma da ferramenta real,  
mas os dados são simulados para fins de aprendizado.
""")

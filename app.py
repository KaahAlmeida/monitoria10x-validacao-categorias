import streamlit as st
import pandas as pd
import random
import re

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
Crie <b>mais de uma categoria</b>, cada uma com <b>até 2 termos</b>, cada termo com <b>slop individual</b>.
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

categorias = []
for i in range(1, 4):
    with st.expander(f"Categoria {i}"):
        nome = st.text_input(f"Nome da Categoria {i}", key=f"nome_{i}")
        termos = []
        for t in range(1, 3):
            termo = st.text_input(f"Termo {t}", key=f"c{i}_t{t}")
            slop = st.slider(f"Slop do termo {t}", 0, 5, 2, key=f"c{i}_s{t}")
            if termo:
                termos.append({"texto": termo, "slop": slop})
        lado = st.selectbox(f"Analisar lado", ["CLIENTE", "AGENTE", "AMBOS"], key=f"c{i}_lado")
        if nome and termos:
            categorias.append({"nome": nome, "termos": termos, "lado": lado})

st.divider()

# =========================
# FUNÇÕES DE MATCH (CORRIGIDAS)
# =========================
def normalizar(texto):
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    return texto.split()

def termo_bate(transcricao, termo, slop):
    trans_tokens = normalizar(transcricao)
    termo_tokens = normalizar(termo)

    if len(termo_tokens) == 1:
        return termo_tokens[0] in trans_tokens

    for i in range(len(trans_tokens)):
        if trans_tokens[i] == termo_tokens[0]:
            idx = i
            ok = True
            for t in termo_tokens[1:]:
                janela = trans_tokens[idx+1 : idx+slop+2]
                if t in janela:
                    idx = idx + 1 + janela.index(t)
                else:
                    ok = False
                    break
            if ok:
                return True
    return False

def valida_categoria(transcricao, termos):
    for termo in termos:
        if termo_bate(transcricao, termo["texto"], termo["slop"]):
            return True
    return False

# =========================
# EXECUÇÃO DA VALIDAÇÃO
# =========================
st.header("3️⃣ Resultados")

if st.button("🔍 Validar Categorias"):

    resultados = []
    metrics = []

    for cat in categorias:
        acertos = 0
        total = 0

        for _, row in df.iterrows():
            if cat["lado"] != "AMBOS" and row["Lado"] != cat["lado"]:
                continue

            acionou = valida_categoria(row["Transcrição"], cat["termos"])
            total += 1

            # CORREÇÃO DA PONTUAÇÃO: agora contabiliza mesmo se o nome for diferente
            if acionou and cat["nome"].lower() in row["Categoria Esperada"].lower():
                acertos += 1

            resultados.append({
                "Categoria": cat["nome"],
                "Transcrição": row["Transcrição"],
                "Acionou": "Sim" if acionou else "Não"
            })

        taxa = round((acertos / total) * 100, 2) if total else 0
        metrics.append({"Categoria": cat["nome"], "Taxa": taxa})

    # =========================
    # MÉTRICAS VISUAIS
    # =========================
    st.markdown("### 📊 Taxa de Acerto por Categoria")
    cols = st.columns(len(metrics))
    for i, m in enumerate(metrics):
        cols[i].markdown(
            f"""
            <div style="background-color:#F9E79F; padding:15px; border-radius:10px; text-align:center">
            <h3>{m["Categoria"]}</h3>
            <h2>{m["Taxa"]}%</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()
    st.markdown("### 📝 Resultados Detalhados")
    st.dataframe(pd.DataFrame(resultados), use_container_width=True)

st.divider()
st.caption("📌 Simulador didático – Monitoria 10x")





















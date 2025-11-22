import json
import requests
import streamlit as st


st.set_page_config(
    page_title="JusCash ML - Análise de Processos",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ JusCash ML - Análise Automatizada de Processos")
st.markdown(
    """
Interface para consumir a API de análise de processos judiciais.
Cole o JSON do processo abaixo e veja a decisão automaticamente.
"""
)


# Sidebar - Config
st.sidebar.header("Configurações")

api_url_default = "http://localhost:8000"
api_url = st.sidebar.text_input(
    "URL da API",
    value=api_url_default,
    help="Endereço base da API FastAPI",
)

modo_debug = st.sidebar.checkbox(
    "Modo debug (mostrar JSON completo de resposta)", value=False
)



# Função para chamar o endpoint /analisar-processo
def chamar_api_analisar_processo(payload: dict) -> dict:

    url = f"{api_url}/analisar-processo"
    resposta = requests.post(url, json=payload, timeout=60)

    if resposta.status_code >= 400:

        try:
            detalhe = resposta.json()
        except Exception:
            detalhe = resposta.text
        raise RuntimeError(f"Erro na API ({resposta.status_code}): {detalhe}")

    return resposta.json()



# Área de entrada de json do processo
st.subheader("Entrada do processo (JSON)")

st.markdown(
    """
Cole aqui o JSON do processo no **formato esperado pela API**.
Você pode usar um dos exemplos fornecidos no case.
"""
)

json_texto = st.text_area(
    "JSON do processo",
    height=300,
    placeholder='{\n  "numeroProcesso": "...",\n  "classe": "...",\n  ...\n}',
)

col1, col2 = st.columns([1, 3])

with col1:
    botao_analisar = st.button("Analisar processo")

with col2:
    st.markdown(
        "<small>Dica: valide se o JSON está bem formatado antes de enviar.</small>",
        unsafe_allow_html=True,
    )


# Lógica principal
if botao_analisar:
    if not json_texto.strip():
        st.error("Por favor, informe o JSON do processo antes de analisar.")
    else:

        try:
            payload = json.loads(json_texto)
        except json.JSONDecodeError as e:
            st.error(f"JSON inválido: {e}")
        else:

            with st.spinner("Analisando processo..."):
                try:
                    resultado = chamar_api_analisar_processo(payload)
                except Exception as e:
                    st.error(f"Erro ao chamar a API: {e}")
                else:

                    st.subheader("Resultado da análise")

                    decisao = resultado.get("decisao")
                    justificativa = resultado.get("justificativa")
                    citacoes = resultado.get("citacoes")

                    # Card da decisao
                    if decisao:
                        if decisao == "approved":
                            cor = "#16a34a"  
                            label = "APROVADO"
                        elif decisao == "rejected":
                            cor = "#dc2626"  
                            label = "REJEITADO"
                        else:
                            cor = "#eab308"  
                            label = decisao.upper()

                        st.markdown(
                            f"""
                            <div style="
                                padding: 12px 16px;
                                border-radius: 8px;
                                background-color: {cor};
                                color: white;
                                display: inline-block;
                                font-weight: 600;">
                                Decisão: {label}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if justificativa:
                        st.markdown("### Justificativa")
                        st.write(justificativa)

                    if citacoes:
                        st.markdown("### Políticas citadas")
                        st.write(", ".join(citacoes))

                    if modo_debug:
                        st.markdown("### JSON completo de resposta")
                        st.json(resultado)

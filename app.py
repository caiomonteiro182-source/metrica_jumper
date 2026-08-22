import datetime
import os
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da Página e Favicon
fav_icon = "logoj.png" if os.path.exists("logoj.png") else "📚"
st.set_page_config(
    page_title="Gestão de Presença | JUMPER",
    page_icon=fav_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS PERSONALIZADA (DARK MODE + JUMPER GREEN)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fundo Escuro Moderno */
    .stApp {
        background-color: #0E1318;
        color: #F1F5F9;
    }
    
    /* Barra Lateral Escura */
    section[data-testid="stSidebar"] {
        background-color: #161C23 !important;
        border-right: 1px solid #232D38;
    }
    
    /* Cards Escuros Estilizados */
    .jumper-card {
        background-color: #161C23;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #232D38;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.25);
        margin-bottom: 20px;
    }
    
    /* Destaque das Caixas de Seleção e Inputs */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] input {
        background-color: #1E2630 !important;
        border: 2px solid #334155 !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    
    div[data-baseweb="select"]:hover > div, div[data-baseweb="input"]:hover input {
        border-color: #A2D136 !important;
    }
    
    /* Rótulos das Caixas de Entrada */
    label {
        color: #A2D136 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Botão Principal em Verde JUMPER (#A2D136) */
    .stButton > button[kind="primary"] {
        background-color: #A2D136 !important;
        color: #0E1318 !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.7rem 1.6rem !important;
        font-size: 16px !important;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 15px rgba(162, 209, 54, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #B5E249 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(162, 209, 54, 0.45);
    }
    
    /* Cards de Métricas no Dashboard */
    [data-testid="stMetric"] {
        background-color: #161C23;
        border: 1px solid #232D38;
        padding: 16px 20px;
        border-radius: 12px;
    }
    
    [data-testid="stMetricValue"] {
        color: #A2D136 !important;
        font-weight: 800 !important;
    }

    /* Ocultar elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 1. BANCO DE DADOS (Criação, Conexão e Auto-Sincronização)
# ---------------------------------------------------------
CONN = sqlite3.connect("jumper_presenca.db", check_same_thread=False)
CURSOR = CONN.cursor()

CURSOR.execute("""
CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    professor TEXT NOT NULL,
    nome_turma TEXT NOT NULL,
    dia_semana TEXT NOT NULL,
    horario TEXT NOT NULL
)
""")

CURSOR.execute("""
CREATE TABLE IF NOT EXISTS presencas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turma_id INTEGER NOT NULL,
    data_aula DATE NOT NULL,
    qtd_alunos INTEGER NOT NULL,
    qtd_presentes INTEGER NOT NULL,
    FOREIGN KEY(turma_id) REFERENCES turmas(id)
)
""")
CONN.commit()

# Lista Completa dos 12 Professores e 25 Turmas Reais da Planilha
turmas_completas = [
    ("ALINE", "Turma ALINE", "Quinta-feira", "19:00 - 21:00"),
    ("CAIO", "Turma CAIO - 1", "Sábado", "08:30 às 10:30"),
    ("CAIO", "Turma CAIO - 2", "Sábado", "10:30 às 12:30"),
    ("CAIO", "Turma CAIO - 3", "Terça-feira", "19:00 às 21:00"),
    ("HELLEN", "Turma HELLEN", "Quarta-feira", "18:30 - 20:30"),
    ("SAMUEL", "Turma SAMUEL", "Sábado", "08:30"),
    ("JULIA", "Turma JULIA", "Sábado", "10:30 às 12:30"),
    ("JURANDIR", "Turma JURANDIR - 1", "Terça-feira", "14:00 às 16:00"),
    ("JURANDIR", "Turma JURANDIR - 2", "Terça-feira", "16:00 às 18:00"),
    ("JURANDIR", "Turma JURANDIR - 3", "Quarta-feira", "14:00 às 16:00"),
    ("KELLY", "Turma KELLY - 1", "Sábado", "08:30 - 10:30"),
    ("KELLY", "Turma KELLY - 2", "Sábado", "10:30 - 12:30"),
    ("KELLY", "Turma KELLY - 3", "Sábado", "13:00 às 15:00"),
    ("KELLY", "Turma KELLY - 4", "Sábado", "16:00 às 18:00"),
    ("MENUHA", "Turma MENUHA", "Sábado", "10:30"),
    ("NAYANE", "Turma NAYANE - 1", "Quarta-feira", "09:00 - 11:00"),
    ("NAYANE", "Turma NAYANE - 2", "Quarta-feira", "16:00 - 18:00"),
    ("NAYANE", "Turma NAYANE - 3", "Quarta-feira", "19:00 - 21:00"),
    ("NAYANE", "Turma NAYANE - 4", "Sábado", "13:00 - 15:00"),
    ("DAVI", "Turma DAVI", "Segunda-feira", "19:00 - 21:00"),
    ("TULIO", "Turma TULIO - 1", "Sábado", "08:30 - 10:30"),
    ("TULIO", "Turma TULIO - 2", "Sábado", "10:30 - 12:30"),
    ("TULIO", "Turma TULIO - 3", "Quarta-feira", "19:00 - 21:00"),
    ("VINICIUS", "Turma VINICIUS - 1", "Sábado", "10:30"),
    ("VINICIUS", "Turma VINICIUS - 2", "Quinta-feira", "09:00"),
]

# Sincronização Inteligente: Adiciona apenas o que ainda não estiver cadastrado no banco
for prof, turma, dia, hora in turmas_completas:
  CURSOR.execute(
      "SELECT COUNT(*) FROM turmas WHERE professor = ? AND nome_turma = ?",
      (prof, turma),
  )
  if CURSOR.fetchone()[0] == 0:
    CURSOR.execute(
        "INSERT INTO turmas (professor, nome_turma, dia_semana, horario)"
        " VALUES (?, ?, ?, ?)",
        (prof, turma, dia, hora),
    )
CONN.commit()

# ---------------------------------------------------------
# 2. BARRA LATERAL (MENU)
# ---------------------------------------------------------
with st.sidebar:
  if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
  else:
    st.markdown(
        "<h2 style='color:#A2D136; font-weight:800;'>JUMPER!</h2>",
        unsafe_allow_html=True,
    )

  st.markdown("<br>", unsafe_allow_html=True)
  menu = st.radio(
      "MENU PRINCIPAL",
      [
          "📝 Lançamento de Aula",
          "🗑️ Excluir / Corrigir Chamada",
          "📊 Dashboard da Gestão",
          "⚙️ Gerenciar Turmas",
      ],
  )
  st.markdown("---")
  st.caption("JUMPER Profissões e Idiomas © 2026")

# ---------------------------------------------------------
# CABEÇALHO COMPACTO COM LOGO "J!"
# ---------------------------------------------------------
col_header1, col_header2 = st.columns([5, 1])
with col_header1:
  st.markdown(
      """
      <div style="margin-bottom: 20px;">
          <h1 style="color: #FFFFFF; font-weight: 800; font-size: 2.2rem; margin: 0;">Frequência de Turmas</h1>
          <p style="color: #94A3B8; font-size: 1rem; margin-top: 4px;">Sistema de lançamento diário de presença e métricas pedagógicas</p>
      </div>
      """,
      unsafe_allow_html=True,
  )
with col_header2:
  if os.path.exists("logoj.png"):
    st.image("logoj.png", width=75)

# ---------------------------------------------------------
# MÓDULO 1: LANÇAMENTO DE PRESENÇA (PROFESSOR)
# ---------------------------------------------------------
if menu == "📝 Lançamento de Aula":
  df_profs = pd.read_sql_query(
      "SELECT DISTINCT professor FROM turmas ORDER BY professor", CONN
  )
  professores = df_profs["professor"].tolist()

  if not professores:
    st.warning("Nenhum professor cadastrado no banco de dados.")
  else:
    prof_selecionado = st.selectbox("👤 Selecione o Professor", professores)

    df_turmas_prof = pd.read_sql_query(
        "SELECT id, nome_turma || ' (' || dia_semana || ' ' || horario || ')'"
        " AS descricao FROM turmas WHERE professor = ?",
        CONN,
        params=(prof_selecionado,),
    )

    if df_turmas_prof.empty:
      st.info("Nenhuma turma encontrada para este professor.")
    else:
      opcoes_turmas = dict(
          zip(df_turmas_prof["descricao"], df_turmas_prof["id"])
      )

      turma_desc = st.selectbox(
          "📚 Selecione a Turma", list(opcoes_turmas.keys())
      )
      turma_id = opcoes_turmas[turma_desc]

      data_aula = st.date_input("📅 Data da Aula", value=datetime.date.today())

      col1, col2 = st.columns(2)
      with col1:
        total_alunos = st.number_input(
            "👥 Total de Alunos da Turma",
            min_value=1,
            value=20,
            step=1,
            key="input_total_alunos",
        )

      with col2:
        total_presentes = st.number_input(
            "✅ Quantidade de Presentes",
            min_value=0,
            max_value=int(total_alunos),
            value=min(16, int(total_alunos)),
            step=1,
            key="input_total_presentes",
        )

      if total_presentes > total_alunos:
        st.error(
            f"❌ Erro: O número de presentes ({total_presentes}) não pode ser"
            f" maior do que o total de alunos na turma ({total_alunos})."
        )
      else:
        porcentagem_presenca = (
            (total_presentes / total_alunos) * 100 if total_alunos > 0 else 0
        )

        if porcentagem_presenca < 80.0:
          cor_texto = "#FF4B4B"
          bg_box = "rgba(255, 75, 75, 0.15)"
          border_color = "#FF4B4B"
        else:
          cor_texto = "#A2D136"
          bg_box = "rgba(162, 209, 54, 0.15)"
          border_color = "#A2D136"

        st.markdown(
            f"""
            <div style="
                background-color: {bg_box};
                border-left: 5px solid {border_color};
                padding: 16px 20px;
                border-radius: 8px;
                margin-top: 15px;
                margin-bottom: 25px;
            ">
                <span style="font-size: 18px; font-weight: 700; color: {cor_texto};">
                    📊 Resumo: Frequência: {porcentagem_presenca:.1f}%
                </span>
                <span style="font-size: 15px; color: #CBD5E1; margin-left: 10px;">
                    (Total da turma: {total_alunos} alunos)
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("💾 Salvar Chamada", type="primary"):
          CURSOR.execute(
              "INSERT INTO presencas (turma_id, data_aula, qtd_alunos,"
              " qtd_presentes) VALUES (?, ?, ?, ?)",
              (
                  turma_id,
                  data_aula.strftime("%Y-%m-%d"),
                  total_alunos,
                  total_presentes,
              ),
          )
          CONN.commit()
          st.success("✅ Chamada salva com sucesso!")

# ---------------------------------------------------------
# MÓDULO 2: EXCLUIR / CORRIGIR CHAMADA
# ---------------------------------------------------------
elif menu == "🗑️ Excluir / Corrigir Chamada":
  st.subheader("🗑️ Gerenciar e Apagar Chamadas")
  st.caption("Selecione um registro efetuado incorretamente para remoção.")

  query_ultimos = """
    SELECT 
        p.id,
        p.data_aula as Data,
        t.professor as Professor,
        t.nome_turma as Turma,
        p.qtd_alunos as "Alunos Esperados",
        p.qtd_presentes as Presentes,
        (p.qtd_alunos - p.qtd_presentes) as Faltas
    FROM presencas p
    JOIN turmas t ON p.turma_id = t.id
    ORDER BY p.id DESC
    LIMIT 50
    """
  df_chamadas = pd.read_sql_query(query_ultimos, CONN)

  if df_chamadas.empty:
    st.info("Nenhuma chamada registrada no histórico para exclusão.")
  else:
    st.dataframe(df_chamadas, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Apagar Lançamento Incorreto")

    opcoes_deletar = {}
    for idx, row in df_chamadas.iterrows():
      label = (
          f"ID: {row['id']} | Data: {row['Data']} | Prof: {row['Professor']} -"
          f" {row['Turma']} ({row['Presentes']}/{row['Alunos Esperados']}"
          " presentes)"
      )
      opcoes_deletar[label] = row["id"]

    chamada_selecionada = st.selectbox(
        "Selecione a chamada que deseja APAGAR:", list(opcoes_deletar.keys())
    )
    id_para_deletar = opcoes_deletar[chamada_selecionada]

    if st.button("❌ Confirmar Exclusão da Chamada", type="primary"):
      CURSOR.execute("DELETE FROM presencas WHERE id = ?", (id_para_deletar,))
      CONN.commit()
      st.success("✅ Chamada apagada com sucesso!")
      st.rerun()

# ---------------------------------------------------------
# MÓDULO 3: DASHBOARD DA GESTÃO
# ---------------------------------------------------------
elif menu == "📊 Dashboard da Gestão":
  query = """
    SELECT 
        p.id,
        t.professor,
        t.nome_turma,
        p.data_aula,
        p.qtd_alunos,
        p.qtd_presentes,
        (p.qtd_alunos - p.qtd_presentes) as qtd_faltas,
        strftime('%Y-%m', p.data_aula) as mes_ano
    FROM presencas p
    JOIN turmas t ON p.turma_id = t.id
    ORDER BY p.data_aula DESC
    """
  df_dados = pd.read_sql_query(query, CONN)

  if df_dados.empty:
    st.info("Nenhum lançamento registrado até o momento.")
  else:
    meses_disponiveis = sorted(df_dados["mes_ano"].unique(), reverse=True)
    mes_selecionado = st.sidebar.selectbox(
        "Filtrar por Mês/Ano", meses_disponiveis
    )

    df_mes = df_dados[df_dados["mes_ano"] == mes_selecionado].copy()

    total_aulas = len(df_mes)
    total_alunos_acum = df_mes["qtd_alunos"].sum()
    total_presentes_acum = df_mes["qtd_presentes"].sum()
    total_faltas_acum = df_mes["qtd_faltas"].sum()

    freq_media_geral = (
        (total_presentes_acum / total_alunos_acum * 100)
        if total_alunos_acum > 0
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Frequência Média Unidade", f"{freq_media_geral:.1f}%")
    c2.metric("Aulas Ministradas", total_aulas)
    c3.metric("Total Alunos Esperados", total_alunos_acum)
    c4.metric("Total Faltas no Mês", total_faltas_acum)

    st.markdown("<br>", unsafe_allow_html=True)

    df_prof = (
        df_mes.groupby("professor")
        .agg(
            total_esperado=("qtd_alunos", "sum"),
            total_presencas=("qtd_presentes", "sum"),
            aulas=("id", "count"),
        )
        .reset_index()
    )

    df_prof["Frequencia_%"] = round(
        (df_prof["total_presencas"] / df_prof["total_esperado"]) * 100, 1
    )

    col_g1, col_g2 = st.columns([2, 1])

    with col_g1:
      fig = px.bar(
          df_prof,
          x="professor",
          y="Frequencia_%",
          text="Frequencia_%",
          title=f"Taxa de Frequência por Professor ({mes_selecionado})",
          color_discrete_sequence=["#A2D136"],
          labels={"Frequencia_%": "Presença (%)", "professor": "Professor"},
      )
      fig.update_traces(
          texttemplate="%{text:.1f}%",
          textposition="outside",
          marker_color="#A2D136",
      )
      fig.update_layout(
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
          font_color="#F1F5F9",
          yaxis_range=[0, 105],
          margin=dict(l=10, r=10, t=40, b=10),
      )
      st.plotly_chart(fig, use_container_width=True)

    with col_g2:
      st.subheader("Resumo por Professor")
      st.dataframe(
          df_prof[["professor", "aulas", "Frequencia_%"]].rename(
              columns={"professor": "Prof.", "aulas": "Aulas"}
          ),
          use_container_width=True,
          hide_index=True,
      )

    st.markdown("---")
    st.subheader("📋 Registros Detalhados do Mês")
    st.dataframe(
        df_mes[[
            "id",
            "data_aula",
            "professor",
            "nome_turma",
            "qtd_alunos",
            "qtd_presentes",
            "qtd_faltas",
        ]],
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------------
# MÓDULO 4: GERENCIAR TURMAS
# ---------------------------------------------------------
elif menu == "⚙️ Gerenciar Turmas":
  st.subheader("⚙️ Cadastro e Gestão de Turmas")

  with st.expander("➕ Cadastrar Nova Turma"):
    with st.form("form_nova_turma", clear_on_submit=True):
      novo_prof = st.text_input("Nome do Professor")
      nome_turma = st.text_input("Nome/Curso da Turma (Ex: Informática)")
      dia_semana = st.selectbox(
          "Dia da Semana",
          [
              "Segunda-feira",
              "Terça-feira",
              "Quarta-feira",
              "Quinta-feira",
              "Sexta-feira",
              "Sábado",
          ],
      )
      horario = st.text_input("Horário (Ex: 08:30 - 10:30)")

      btn_cadastrar = st.form_submit_button("Cadastrar Turma", type="primary")

      if btn_cadastrar:
        if novo_prof and nome_turma and horario:
          CURSOR.execute(
              "INSERT INTO turmas (professor, nome_turma, dia_semana, horario)"
              " VALUES (?, ?, ?, ?)",
              (novo_prof.upper(), nome_turma, dia_semana, horario),
          )
          CONN.commit()
          st.success("Turma cadastrada com sucesso!")
          st.rerun()
        else:
          st.error("Preencha todos os campos obrigatórios.")

  st.markdown("<br>", unsafe_allow_html=True)
  st.subheader("Turmas Atualmente Cadastradas")
  df_todas_turmas = pd.read_sql_query(
      "SELECT id, professor, nome_turma, dia_semana, horario FROM turmas"
      " ORDER BY professor",
      CONN,
  )
  st.dataframe(df_todas_turmas, use_container_width=True, hide_index=True)

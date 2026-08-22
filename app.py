import datetime
import os
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração Inicial da Página e Favicon
fav_icon = "logoj.png" if os.path.exists("logoj.png") else "📚"
st.set_page_config(
    page_title="Frequência JUMPER",
    page_icon=fav_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS PERSONALIZADA (Identidade JUMPER)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* Cores Institucionais: Verde JUMPER (#A2D136), Dark (#13171C), Card (#1E232A) */
    :root {
        --primary-color: #A2D136;
        --bg-dark: #13171C;
        --card-bg: #1E232A;
    }
    
    /* Ajustes Gerais de Fundo e Texto */
    .stApp {
        background-color: #13171C;
        color: #F0F2F5;
    }
    
    /* Estilização da Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #1A1F26 !important;
        border-right: 1px solid #2B323B;
    }
    
    /* Customização dos Botões Principais */
    .stButton > button[kind="primary"] {
        background-color: #A2D136 !important;
        color: #13171C !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #B5E249 !important;
        transform: translateY(-2px);
        box-shadow: 0px 4px 12px rgba(162, 209, 54, 0.3);
    }
    
    /* Inputs e Formatações de Leitura */
    div[data-baseweb="input"] input, div[data-baseweb="select"] {
        border-radius: 8px !important;
    }
    
    /* Ocultar elementos padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 1. BANCO DE DADOS (Criação e Conexão)
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

# Carga inicial de turmas
CURSOR.execute("SELECT COUNT(*) FROM turmas")
if CURSOR.fetchone()[0] == 0:
  turmas_iniciais = [
      ("ALINE", "CABELEIREIRO", "Quinta-feira", "19:00 - 21:00"),
      ("CAIO", "INFORMÁTICA - T1", "Sábado", "08:30 - 10:30"),
      ("CAIO", "INFORMÁTICA - T2", "Sábado", "10:30 - 12:30"),
      ("CAIO", "INFORMÁTICA - T3", "Terça-feira", "19:00 - 21:00"),
      ("HELLEN", "INGLÊS", "Quarta-feira", "14:00 - 16:00"),
      ("JULIA", "ADMINISTRAÇÃO", "Sábado", "08:30 - 10:30"),
      ("JURANDIR", "ROBÓTICA", "Sábado", "13:30 - 15:30"),
      ("KELLY", "DESIGN", "Sexta-feira", "19:00 - 21:00"),
  ]
  CURSOR.executemany(
      "INSERT INTO turmas (professor, nome_turma, dia_semana, horario) VALUES"
      " (?, ?, ?, ?)",
      turmas_iniciais,
  )
  CONN.commit()

# ---------------------------------------------------------
# 2. LOGO E NAVEGAÇÃO NA LATERAL
# ---------------------------------------------------------
with st.sidebar:
  if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
  else:
    st.title("JUMPER!")

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
# MÓDULO 1: LANÇAMENTO DE PRESENÇA
# ---------------------------------------------------------
if menu == "📝 Lançamento de Aula":
  st.title("📝 Lançamento de Presença")
  st.caption("Selecione o professor e informe os dados da chamada da aula.")

  df_profs = pd.read_sql_query(
      "SELECT DISTINCT professor FROM turmas ORDER BY professor", CONN
  )
  professores = df_profs["professor"].tolist()

  if not professores:
    st.warning("Nenhum professor cadastrado no banco de dados.")
  else:
    prof_selecionado = st.selectbox("Selecione o Professor", professores)

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

      turma_desc = st.selectbox("Selecione a Turma", list(opcoes_turmas.keys()))
      turma_id = opcoes_turmas[turma_desc]

      data_aula = st.date_input("Data da Aula", value=datetime.date.today())

      col1, col2 = st.columns(2)
      with col1:
        total_alunos = st.number_input(
            "Total de Alunos da Turma",
            min_value=1,
            value=20,
            step=1,
            key="input_total_alunos",
        )

      with col2:
        total_presentes = st.number_input(
            "Quantidade de Presentes",
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
          bg_box = "rgba(255, 75, 75, 0.12)"
          border_color = "#FF4B4B"
        else:
          cor_texto = "#A2D136"
          bg_box = "rgba(162, 209, 54, 0.12)"
          border_color = "#A2D136"

        st.markdown(
            f"""
            <div style="
                background-color: {bg_box};
                border-left: 5px solid {border_color};
                padding: 14px 18px;
                border-radius: 8px;
                margin-top: 10px;
                margin-bottom: 20px;
            ">
                <span style="font-size: 17px; font-weight: bold; color: {cor_texto};">
                    📊 Resumo: Frequência: {porcentagem_presenca:.1f}%
                </span>
                <span style="font-size: 15px; color: #D0D4DC; margin-left: 8px;">
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
  st.title("🗑️ Gerenciar e Apagar Chamadas")
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
    st.subheader("Últimas Chamadas Registradas")
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

    btn_deletar = st.button("❌ Confirmar Exclusão da Chamada", type="primary")

    if btn_deletar:
      CURSOR.execute("DELETE FROM presencas WHERE id = ?", (id_para_deletar,))
      CONN.commit()
      st.success("✅ Chamada apagada com sucesso!")
      st.rerun()

# ---------------------------------------------------------
# MÓDULO 3: DASHBOARD DA GESTÃO
# ---------------------------------------------------------
elif menu == "📊 Dashboard da Gestão":
  st.title("📊 Painel de Controle de Frequência")

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
    c3.metric("Total de Alunos Esperados", total_alunos_acum)
    c4.metric("Total de Faltas", total_faltas_acum)

    st.markdown("---")

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
      # Gráfico customizado com a cor institucional verde JUMPER
      fig = px.bar(
          df_prof,
          x="professor",
          y="Frequencia_%",
          text="Frequencia_%",
          title=f"Frequência por Professor - {mes_selecionado}",
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
          font_color="#F0F2F5",
          yaxis_range=[0, 105],
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
  st.title("⚙️ Cadastro e Gestão de Turmas")

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

  st.subheader("Turmas Atualmente Cadastradas")
  df_todas_turmas = pd.read_sql_query(
      "SELECT id, professor, nome_turma, dia_semana, horario FROM turmas"
      " ORDER BY professor",
      CONN,
  )
  st.dataframe(df_todas_turmas, use_container_width=True, hide_index=True)

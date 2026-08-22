import datetime
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração Inicial da Página
st.set_page_config(
    page_title="Gestão de Presença - JUMPER", page_icon="📚", layout="wide"
)

# ---------------------------------------------------------
# 1. BANCO DE DADOS (Criação e Conexão)
# ---------------------------------------------------------
CONN = sqlite3.connect("jumper_presenca.db", check_same_thread=False)
CURSOR = CONN.cursor()

# Tabela de Turmas
CURSOR.execute("""
CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    professor TEXT NOT NULL,
    nome_turma TEXT NOT NULL,
    dia_semana TEXT NOT NULL,
    horario TEXT NOT NULL
)
""")

# Tabela de Presenças (Lançamentos Diários)
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

# Carga inicial de turmas (com base na planilha) se o banco estiver vazio
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
# 2. INTERFACE E NAVEGAÇÃO
# ---------------------------------------------------------
st.sidebar.title("📚 JUMPER - Sistema")
menu = st.sidebar.radio(
    "Navegação",
    [
        "📝 Lançamento de Aula",
        "🗑️ Excluir / Corrigir Chamada",
        "📊 Dashboard da Gestão",
        "⚙️ Gerenciar Turmas",
    ],
)

# ---------------------------------------------------------
# MÓDULO 1: LANÇAMENTO DE PRESENÇA (PROFESSOR)
# ---------------------------------------------------------
if menu == "📝 Lançamento de Aula":
  st.title("📝 Lançamento de Presença")
  st.caption("Selecione o seu nome e preencha a frequência da aula do dia.")

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
            value=min(8, int(total_alunos)),
            step=1,
            key="input_total_presentes",
        )

      # Validação e Cor Condicional
      if total_presentes > total_alunos:
        st.error(
            f"❌ Erro: O número de presentes ({total_presentes}) não pode ser"
            f" maior do que o total de alunos na turma ({total_alunos})."
        )
      else:
        porcentagem_presenca = (
            (total_presentes / total_alunos) * 100 if total_alunos > 0 else 0
        )

        # Regra de Cor: Menor que 80% fica Vermelho, maior/igual a 80% fica Verde
        if porcentagem_presenca < 80.0:
          cor_texto = "#FF2B2B"  # Vermelho
          bg_box = "rgba(255, 43, 43, 0.1)"
          border_color = "#FF2B2B"
        else:
          cor_texto = "#00C853"  # Verde
          bg_box = "rgba(0, 200, 83, 0.1)"
          border_color = "#00C853"

        # Exibição estilizada em HTML/CSS no Streamlit
        st.markdown(
            f"""
            <div style="
                background-color: {bg_box};
                border-left: 5px solid {border_color};
                padding: 12px 16px;
                border-radius: 6px;
                margin-bottom: 16px;
            ">
                <span style="font-size: 16px; font-weight: bold; color: {cor_texto};">
                    📊 Resumo: Frequência: {porcentagem_presenca:.1f}%
                </span>
                <span style="font-size: 15px; color: #CCCCCC; margin-left: 8px;">
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
  st.caption(
      "Caso tenha lançado algum valor errado, selecione o registro abaixo para"
      " excluir."
  )

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
# MÓDULO 3: DASHBOARD (GESTÃO / COORDENAÇÃO)
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
      fig = px.bar(
          df_prof,
          x="professor",
          y="Frequencia_%",
          text="Frequencia_%",
          title=f"Frequência por Professor - {mes_selecionado}",
          color="Frequencia_%",
          color_continuous_scale="Greens",
          labels={"Frequencia_%": "Presença (%)", "professor": "Professor"},
      )
      fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
      fig.update_layout(yaxis_range=[0, 105])
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

      btn_cadastrar = st.form_submit_button("Cadastrar Turma")

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

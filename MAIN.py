import os
import sys
import json
import re
import shutil

from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QColor, QPalette, QTextOption
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QPlainTextEdit, QProgressBar, QFileDialog,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QSizePolicy, QScrollArea
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT-DLP GUI Prototipo")
        self.resize(1400, 860)
        self.setMinimumSize(980, 700)

        self.process = None
        self.analysis_process = None
        self.playlist_entries = []
        self.analysis_buffer = ""
        self.action_buttons = []

        self.setStyleSheet(self.build_stylesheet())
        self.build_ui()
        self.connect_signals()
        self.atualizar_opcoes_qualidade(self.combo_tipo.currentText())
        self.verificar_dependencias()
        self.atualizar_preview_comando()
        self.atualizar_resumo()
        self.set_running_state(False)
        self.reflow_action_buttons()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        top_layout = QHBoxLayout()
        self.lbl_titulo = QLabel("YT-DLP GUI")
        self.lbl_titulo.setObjectName("TitleLabel")
        self.lbl_subtitulo = QLabel("Frontend visual para yt-dlp com playlist, preview de comando e execução assistida")
        self.lbl_subtitulo.setObjectName("SubTitleLabel")

        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(2)
        title_wrap.addWidget(self.lbl_titulo)
        title_wrap.addWidget(self.lbl_subtitulo)

        self.lbl_status = QLabel("Status: verificando dependências...")
        self.lbl_status.setObjectName("StatusLabel")

        top_layout.addLayout(title_wrap)
        top_layout.addStretch()
        top_layout.addWidget(self.lbl_status)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        self.left_scroll = QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        self.left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_scroll.setFrameShape(QScrollArea.NoFrame)
        self.left_scroll.setMinimumWidth(420)
        self.left_scroll.setMaximumWidth(520)
        self.left_scroll.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        left_container = QWidget()
        self.left_scroll.setWidget(left_container)
        left_panel = QVBoxLayout(left_container)
        left_panel.setSpacing(12)
        left_panel.setContentsMargins(0, 0, 0, 0)

        group_url = QGroupBox("Fonte")
        url_layout = QVBoxLayout(group_url)
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Cole a URL do vídeo ou playlist")
        self.lbl_playlist_status = QLabel("Nenhuma playlist analisada.")
        self.lbl_playlist_status.setObjectName("HintLabel")
        url_layout.addWidget(QLabel("URL"))
        url_layout.addWidget(self.input_url)
        url_layout.addWidget(self.lbl_playlist_status)

        group_download = QGroupBox("Opções de download")
        download_layout = QGridLayout(group_download)
        download_layout.setHorizontalSpacing(10)
        download_layout.setVerticalSpacing(10)
        download_layout.setColumnStretch(0, 0)
        download_layout.setColumnStretch(1, 1)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Vídeo", "MP3"])

        self.combo_qualidade = QComboBox()

        self.input_nome_arquivo = QLineEdit()
        self.input_nome_arquivo.setPlaceholderText("Opcional, sem extensão")

        self.check_playlist = QCheckBox("🎞️ Tratar URL como playlist")
        self.check_embed_thumb = QCheckBox("🖼️ Inserir thumbnail e metadata quando possível")
        self.check_embed_thumb.setChecked(True)

        lbl_tipo = QLabel("Tipo")
        lbl_qualidade = QLabel("Qualidade")
        lbl_nome = QLabel("Nome do arquivo")
        lbl_tipo.setMinimumWidth(95)
        lbl_qualidade.setMinimumWidth(95)
        lbl_nome.setMinimumWidth(95)

        download_layout.addWidget(lbl_tipo, 0, 0)
        download_layout.addWidget(self.combo_tipo, 0, 1)
        download_layout.addWidget(lbl_qualidade, 1, 0)
        download_layout.addWidget(self.combo_qualidade, 1, 1)
        download_layout.addWidget(lbl_nome, 2, 0)
        download_layout.addWidget(self.input_nome_arquivo, 2, 1)
        download_layout.addWidget(self.check_playlist, 3, 0, 1, 2)
        download_layout.addWidget(self.check_embed_thumb, 4, 0, 1, 2)

        group_destino = QGroupBox("Destino")
        destino_layout = QHBoxLayout(group_destino)
        self.input_pasta = QLineEdit()
        self.input_pasta.setPlaceholderText("Selecione a pasta de saída")
        self.btn_procurar = QPushButton("📁 Procurar")
        self.btn_procurar.setMinimumWidth(110)
        destino_layout.addWidget(self.input_pasta, 1)
        destino_layout.addWidget(self.btn_procurar, 0)

        group_actions = QGroupBox("Ações")
        self.actions_layout = QGridLayout(group_actions)
        self.actions_layout.setHorizontalSpacing(10)
        self.actions_layout.setVerticalSpacing(10)

        self.btn_analisar = QPushButton("🔎 Analisar playlist")
        self.btn_marcar_todos = QPushButton("✅ Marcar todos")
        self.btn_desmarcar_todos = QPushButton("⬜ Desmarcar todos")
        self.btn_baixar = QPushButton("⬇️ Baixar")
        self.btn_cancelar = QPushButton("🛑 Cancelar")
        self.btn_limpar = QPushButton("🧹 Limpar")
        self.btn_baixar.setObjectName("PrimaryButton")
        self.btn_cancelar.setObjectName("DangerButton")

        self.action_buttons = [
            self.btn_analisar,
            self.btn_marcar_todos,
            self.btn_desmarcar_todos,
            self.btn_baixar,
            self.btn_cancelar,
            self.btn_limpar,
        ]

        for btn in self.action_buttons:
            btn.setMinimumHeight(42)
            btn.setMinimumWidth(150)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        group_summary = QGroupBox("Resumo")
        summary_layout = QVBoxLayout(group_summary)
        self.txt_resumo = QPlainTextEdit()
        self.txt_resumo.setReadOnly(True)
        self.txt_resumo.setMinimumHeight(92)
        self.txt_resumo.setMaximumHeight(120)
        self.txt_resumo.setWordWrapMode(QTextOption.WordWrap)
        summary_layout.addWidget(self.txt_resumo)

        group_preview = QGroupBox("Comando gerado")
        preview_layout = QVBoxLayout(group_preview)
        self.txt_comando = QPlainTextEdit()
        self.txt_comando.setReadOnly(True)
        self.txt_comando.setPlaceholderText("O comando gerado aparecerá aqui.")
        self.txt_comando.setMinimumHeight(95)
        self.txt_comando.setMaximumHeight(140)
        self.txt_comando.setWordWrapMode(QTextOption.WrapAnywhere)
        preview_layout.addWidget(self.txt_comando)

        group_info = QGroupBox("Informações")
        info_layout = QVBoxLayout(group_info)
        self.txt_info = QPlainTextEdit()
        self.txt_info.setReadOnly(True)
        self.txt_info.setMinimumHeight(95)
        self.txt_info.setMaximumHeight(130)
        self.txt_info.setPlainText(
            "Fluxo sugerido:\n"
            "1. Cole a URL.\n"
            "2. Analise a playlist, se necessário.\n"
            "3. Marque os itens desejados.\n"
            "4. Revise o comando gerado.\n"
            "5. Clique em Baixar."
        )
        info_layout.addWidget(self.txt_info)

        left_panel.addWidget(group_url)
        left_panel.addWidget(group_download)
        left_panel.addWidget(group_destino)
        left_panel.addWidget(group_actions)
        left_panel.addWidget(group_summary)
        left_panel.addWidget(group_preview)
        left_panel.addWidget(group_info)
        left_panel.addStretch()

        right_widget = QWidget()
        right_panel = QVBoxLayout(right_widget)
        right_panel.setSpacing(12)
        right_panel.setContentsMargins(0, 0, 0, 0)

        group_playlist = QGroupBox("Itens da playlist")
        playlist_layout = QVBoxLayout(group_playlist)
        toolbar_layout = QHBoxLayout()
        self.input_filtro = QLineEdit()
        self.input_filtro.setPlaceholderText("Filtrar por título...")
        self.lbl_qtd_itens = QLabel("0 itens")
        self.lbl_qtd_itens.setObjectName("HintLabel")
        toolbar_layout.addWidget(self.input_filtro, 1)
        toolbar_layout.addWidget(self.lbl_qtd_itens, 0)

        self.table_playlist = QTableWidget(0, 5)
        self.table_playlist.setHorizontalHeaderLabels(["Baixar", "#", "Título", "Duração", "ID"])
        self.table_playlist.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_playlist.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_playlist.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_playlist.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_playlist.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table_playlist.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_playlist.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_playlist.verticalHeader().setVisible(False)
        self.table_playlist.setAlternatingRowColors(True)
        self.table_playlist.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_playlist.setMinimumHeight(300)
        self.table_playlist.setWordWrap(False)

        playlist_layout.addLayout(toolbar_layout)
        playlist_layout.addWidget(self.table_playlist, 1)

        group_progress = QGroupBox("Execução")
        progress_layout = QVBoxLayout(group_progress)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(24)
        self.txt_log = QPlainTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setPlaceholderText("Logs do yt-dlp aparecerão aqui.")
        self.txt_log.setMinimumHeight(190)
        self.txt_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.txt_log, 1)

        right_panel.addWidget(group_playlist, 3)
        right_panel.addWidget(group_progress, 2)

        body_layout.addWidget(self.left_scroll, 0)
        body_layout.addWidget(right_widget, 1)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(body_layout, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reflow_action_buttons()

    def reflow_action_buttons(self):
        if not hasattr(self, "actions_layout"):
            return

        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        available_width = self.left_scroll.viewport().width() if self.left_scroll else self.width()
        if available_width >= 520:
            columns = 3
        elif available_width >= 360:
            columns = 2
        else:
            columns = 1

        for index, btn in enumerate(self.action_buttons):
            row = index // columns
            col = index % columns
            self.actions_layout.addWidget(btn, row, col)

    def connect_signals(self):
        self.btn_procurar.clicked.connect(self.selecionar_pasta)
        self.btn_analisar.clicked.connect(self.analisar_playlist)
        self.btn_marcar_todos.clicked.connect(lambda: self.marcar_todos(True))
        self.btn_desmarcar_todos.clicked.connect(lambda: self.marcar_todos(False))
        self.btn_baixar.clicked.connect(self.iniciar_download)
        self.btn_cancelar.clicked.connect(self.cancelar_processo)
        self.btn_limpar.clicked.connect(self.limpar_tudo)

        self.input_url.textChanged.connect(self.sync_ui_state)
        self.input_pasta.textChanged.connect(self.sync_ui_state)
        self.input_nome_arquivo.textChanged.connect(self.sync_ui_state)
        self.check_playlist.stateChanged.connect(self.sync_ui_state)
        self.check_embed_thumb.stateChanged.connect(self.sync_ui_state)
        self.combo_tipo.currentTextChanged.connect(self.atualizar_opcoes_qualidade)
        self.combo_qualidade.currentTextChanged.connect(self.sync_ui_state)
        self.input_filtro.textChanged.connect(self.aplicar_filtro_playlist)
        self.table_playlist.itemChanged.connect(self.on_playlist_item_changed)

    def build_stylesheet(self):
        return """
        QWidget {
            background: #141824;
            color: #e7ecf3;
            font-size: 13px;
        }
        QMainWindow {
            background: #141824;
        }
        QGroupBox {
            border: 1px solid #2a3448;
            border-radius: 10px;
            margin-top: 10px;
            padding-top: 12px;
            background: #1b2130;
            font-weight: 600;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 4px;
            color: #9fb4d9;
        }
        QLabel {
            background: transparent;
        }
        QLabel#TitleLabel {
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
        }
        QLabel#SubTitleLabel {
            color: #95a8c7;
            font-size: 12px;
        }
        QLabel#StatusLabel {
            color: #b8c7e0;
            padding: 6px 10px;
            border: 1px solid #2b3b53;
            border-radius: 8px;
            background: #18202d;
            font-weight: 600;
        }
        QLabel#HintLabel {
            color: #9aa8bf;
        }
        QLineEdit, QComboBox, QPlainTextEdit, QTableWidget {
            background: #111722;
            border: 1px solid #2a3448;
            border-radius: 8px;
            padding: 8px;
            color: #edf2ff;
            selection-background-color: #38598b;
        }
        QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {
            border: 1px solid #4d7dd6;
        }
        QPushButton {
            background: #243145;
            border: 1px solid #334764;
            border-radius: 8px;
            padding: 10px 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #2b3b53;
        }
        QPushButton:disabled {
            color: #8694aa;
            background: #202736;
            border: 1px solid #2a3448;
        }
        QPushButton#PrimaryButton {
            background: #0d6efd;
            border: 1px solid #3d84ff;
            color: white;
        }
        QPushButton#PrimaryButton:hover {
            background: #1f78ff;
        }
        QPushButton#DangerButton {
            background: #7a2030;
            border: 1px solid #a53a50;
            color: white;
        }
        QPushButton#DangerButton:hover {
            background: #91293c;
        }
        QProgressBar {
            border: 1px solid #2a3448;
            border-radius: 8px;
            text-align: center;
            background: #111722;
            min-height: 24px;
            font-weight: 700;
        }
        QProgressBar::chunk {
            border-radius: 7px;
            background: #0d6efd;
        }
        QHeaderView::section {
            background: #20283a;
            color: #dbe6ff;
            padding: 8px;
            border: none;
            border-right: 1px solid #2e3b52;
            border-bottom: 1px solid #2e3b52;
            font-weight: 700;
        }
        QTableWidget {
            gridline-color: #243145;
            alternate-background-color: #161d2b;
        }
        QTableWidget::item:selected {
            background: #26446f;
        }
        QCheckBox {
            spacing: 8px;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        """

    def sync_ui_state(self):
        self.atualizar_preview_comando()
        self.atualizar_resumo()

    def verificar_dependencias(self):
        yt_dlp_ok = shutil.which("yt-dlp") is not None
        ffmpeg_ok = shutil.which("ffmpeg") is not None
        p1 = "yt-dlp OK" if yt_dlp_ok else "yt-dlp AUSENTE"
        p2 = "ffmpeg OK" if ffmpeg_ok else "ffmpeg AUSENTE"
        self.lbl_status.setText(f"Status: {p1} | {p2}")

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta de saída")
        if pasta:
            self.input_pasta.setText(pasta)

    def atualizar_opcoes_qualidade(self, tipo):
        self.combo_qualidade.blockSignals(True)
        self.combo_qualidade.clear()
        if tipo == "MP3":
            self.combo_qualidade.addItems(["Melhor VBR", "320 kbps", "192 kbps", "128 kbps"])
        else:
            self.combo_qualidade.addItems(["Melhor", "1080p", "720p", "480p"])
        self.combo_qualidade.blockSignals(False)
        self.sync_ui_state()

    def atualizar_resumo(self):
        tipo = self.combo_tipo.currentText()
        qualidade = self.combo_qualidade.currentText()
        nome = self.input_nome_arquivo.text().strip() or "automático"
        pasta = self.input_pasta.text().strip() or "pasta atual"
        playlist = "sim" if self.check_playlist.isChecked() else "não"
        extras = "sim" if self.check_embed_thumb.isChecked() else "não"

        self.txt_resumo.setPlainText(
            f"Tipo: {tipo} | Qualidade: {qualidade}\n"
            f"Nome: {nome}\n"
            f"Destino: {pasta}\n"
            f"Playlist: {playlist} | Thumbnail/metadata: {extras}"
        )

    def gerar_output_template(self):
        pasta = self.input_pasta.text().strip()
        nome = self.input_nome_arquivo.text().strip()
        base = f"{nome}.%(ext)s" if nome else "%(title)s.%(ext)s"
        return os.path.join(pasta, base) if pasta else base

    def get_selected_playlist_items(self):
        itens = []
        for row in range(self.table_playlist.rowCount()):
            item_check = self.table_playlist.item(row, 0)
            if item_check and item_check.checkState() == Qt.Checked and not self.table_playlist.isRowHidden(row):
                idx_item = self.table_playlist.item(row, 1)
                if idx_item:
                    itens.append(idx_item.text())
        return itens

    def build_command(self):
        url = self.input_url.text().strip()
        if not url:
            return []

        cmd = ["yt-dlp", "-o", self.gerar_output_template()]

        tipo = self.combo_tipo.currentText()
        qualidade = self.combo_qualidade.currentText()
        selected_items = self.get_selected_playlist_items()
        is_playlist_mode = self.check_playlist.isChecked() or len(self.playlist_entries) > 0

        if not is_playlist_mode:
            cmd.append("--no-playlist")
        elif selected_items and len(selected_items) != len(self.playlist_entries):
            cmd += ["--playlist-items", ",".join(selected_items)]

        if tipo == "MP3":
            cmd += ["-x", "--audio-format", "mp3"]
            mapa_audio = {
                "Melhor VBR": "0",
                "320 kbps": "320K",
                "192 kbps": "192K",
                "128 kbps": "128K",
            }
            cmd += ["--audio-quality", mapa_audio.get(qualidade, "0")]
            if self.check_embed_thumb.isChecked():
                cmd += ["--embed-thumbnail", "--embed-metadata"]
        else:
            mapa_video = {
                "Melhor": "bv*+ba/b",
                "1080p": "bv*[height<=1080]+ba/b[height<=1080]",
                "720p": "bv*[height<=720]+ba/b[height<=720]",
                "480p": "bv*[height<=480]+ba/b[height<=480]",
            }
            cmd += ["-f", mapa_video.get(qualidade, "bv*+ba/b")]
            if self.check_embed_thumb.isChecked():
                cmd += ["--embed-metadata"]

        cmd.append(url)
        return cmd

    def atualizar_preview_comando(self):
        cmd = self.build_command()
        self.txt_comando.setPlainText(" ".join(f'"{c}"' if " " in c else c for c in cmd))

    def analisar_playlist(self):
        if self.analysis_process is not None or self.process is not None:
            QMessageBox.warning(self, "Aguarde", "Já existe um processo em execução.")
            return
        if shutil.which("yt-dlp") is None:
            QMessageBox.critical(self, "Erro", "yt-dlp não encontrado no sistema.")
            return

        url = self.input_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Campo obrigatório", "Informe a URL da playlist.")
            return

        self.analysis_buffer = ""
        self.playlist_entries = []
        self.table_playlist.blockSignals(True)
        self.table_playlist.setRowCount(0)
        self.table_playlist.blockSignals(False)
        self.lbl_playlist_status.setText("Analisando playlist...")
        self.lbl_qtd_itens.setText("0 itens")
        self.txt_log.appendPlainText("Analisando playlist...")

        self.analysis_process = QProcess(self)
        self.analysis_process.setProgram("yt-dlp")
        self.analysis_process.setArguments(["--flat-playlist", "-J", url])
        self.analysis_process.readyReadStandardOutput.connect(self.handle_analysis_stdout)
        self.analysis_process.readyReadStandardError.connect(self.handle_analysis_stderr)
        self.analysis_process.finished.connect(self.analysis_finished)
        self.analysis_process.start()

        self.set_running_state(True)

    def handle_analysis_stdout(self):
        if self.analysis_process is None:
            return
        data = self.analysis_process.readAllStandardOutput()
        self.analysis_buffer += bytes(data).decode("utf-8", errors="replace")

    def handle_analysis_stderr(self):
        if self.analysis_process is None:
            return
        data = self.analysis_process.readAllStandardError()
        text = bytes(data).decode("utf-8", errors="replace")
        if text.strip():
            self.txt_log.appendPlainText(text.strip())

    def analysis_finished(self, exit_code, _exit_status):
        try:
            if exit_code != 0:
                QMessageBox.warning(self, "Falha", "Não foi possível analisar a playlist.")
                self.lbl_playlist_status.setText("Falha ao analisar playlist.")
                return

            payload = json.loads(self.analysis_buffer)
            entries = payload.get("entries", []) if isinstance(payload, dict) else []
            self.playlist_entries = []

            for i, entry in enumerate(entries, start=1):
                title = entry.get("title") or f"Item {i}"
                duration = self.format_duration(entry.get("duration"))
                vid = entry.get("id", "")
                self.playlist_entries.append({
                    "index": i,
                    "title": title,
                    "duration": duration,
                    "id": vid,
                })

            self.populate_playlist_table()
            self.check_playlist.setChecked(True)
            self.lbl_playlist_status.setText(f"Playlist analisada com sucesso: {len(self.playlist_entries)} itens.")
            self.lbl_qtd_itens.setText(f"{len(self.playlist_entries)} itens")
            self.sync_ui_state()
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao processar JSON da playlist:\n{exc}")
            self.lbl_playlist_status.setText("Erro ao processar playlist.")
        finally:
            self.analysis_process = None
            self.set_running_state(False)

    def populate_playlist_table(self):
        self.table_playlist.blockSignals(True)
        self.table_playlist.setRowCount(0)
        for entry in self.playlist_entries:
            row = self.table_playlist.rowCount()
            self.table_playlist.insertRow(row)

            item_check = QTableWidgetItem()
            item_check.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item_check.setCheckState(Qt.Checked)
            self.table_playlist.setItem(row, 0, item_check)

            item_index = QTableWidgetItem(str(entry["index"]))
            item_duration = QTableWidgetItem(entry["duration"])
            item_id = QTableWidgetItem(entry["id"])
            item_title = QTableWidgetItem(entry["title"])
            item_title.setToolTip(entry["title"])

            self.table_playlist.setItem(row, 1, item_index)
            self.table_playlist.setItem(row, 2, item_title)
            self.table_playlist.setItem(row, 3, item_duration)
            self.table_playlist.setItem(row, 4, item_id)
        self.table_playlist.blockSignals(False)

    def aplicar_filtro_playlist(self):
        termo = self.input_filtro.text().strip().lower()
        visible = 0
        for row in range(self.table_playlist.rowCount()):
            title_item = self.table_playlist.item(row, 2)
            text = title_item.text().lower() if title_item else ""
            hide = termo not in text
            self.table_playlist.setRowHidden(row, hide)
            if not hide:
                visible += 1
        total = self.table_playlist.rowCount()
        self.lbl_qtd_itens.setText(f"{visible} visíveis / {total} itens" if total else "0 itens")
        self.sync_ui_state()

    def marcar_todos(self, checked):
        self.table_playlist.blockSignals(True)
        state = Qt.Checked if checked else Qt.Unchecked
        for row in range(self.table_playlist.rowCount()):
            if not self.table_playlist.isRowHidden(row):
                item_check = self.table_playlist.item(row, 0)
                if item_check:
                    item_check.setCheckState(state)
        self.table_playlist.blockSignals(False)
        self.sync_ui_state()

    def on_playlist_item_changed(self, item):
        if item and item.column() == 0:
            self.sync_ui_state()

    def iniciar_download(self):
        if self.process is not None or self.analysis_process is not None:
            QMessageBox.warning(self, "Aguarde", "Já existe um processo em execução.")
            return
        if shutil.which("yt-dlp") is None:
            QMessageBox.critical(self, "Erro", "yt-dlp não encontrado no sistema.")
            return
        if self.combo_tipo.currentText() == "MP3" and shutil.which("ffmpeg") is None:
            QMessageBox.critical(self, "Erro", "ffmpeg é necessário para MP3.")
            return

        if not self.input_pasta.text().strip():
            QMessageBox.warning(
            self,
            "Campo obrigatório",
            "Selecione uma pasta de saída antes de baixar."
        )
        return


        url = self.input_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Campo obrigatório", "Informe uma URL.")
            return

        if self.playlist_entries:
            selected = self.get_selected_playlist_items()
            if not selected:
                QMessageBox.warning(self, "Nenhum item marcado", "Marque pelo menos um item da playlist para baixar.")
                return

        cmd = self.build_command()
        if not cmd:
            QMessageBox.warning(self, "Erro", "Não foi possível gerar o comando.")
            return

        self.txt_log.clear()
        self.progress_bar.setValue(0)
        self.txt_log.appendPlainText("Iniciando download...")
        self.txt_log.appendPlainText(self.txt_comando.toPlainText())
        self.txt_log.appendPlainText("")

        self.process = QProcess(self)
        self.process.setProgram(cmd[0])
        self.process.setArguments(cmd[1:])
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.download_finished)
        self.process.start()

        self.set_running_state(True)

    def handle_stdout(self):
        if self.process is None:
            return
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="replace")
        if text.strip():
            self.txt_log.appendPlainText(text.strip())
            self.atualizar_progresso_por_texto(text)

    def handle_stderr(self):
        if self.process is None:
            return
        data = self.process.readAllStandardError()
        text = bytes(data).decode("utf-8", errors="replace")
        if text.strip():
            self.txt_log.appendPlainText(text.strip())
            self.atualizar_progresso_por_texto(text)

    def atualizar_progresso_por_texto(self, texto):
        matches = re.findall(r"(\d+(?:\.\d+)?)%", texto.replace(",", "."))
        if matches:
            try:
                self.progress_bar.setValue(int(float(matches[-1])))
            except ValueError:
                pass

    def download_finished(self, exit_code, _exit_status):
        self.txt_log.appendPlainText("")
        self.txt_log.appendPlainText(f"Processo finalizado. Código de saída: {exit_code}")
        if exit_code == 0:
            self.progress_bar.setValue(100)
        self.process = None
        self.set_running_state(False)

    def cancelar_processo(self):
        if self.process is not None:
            self.txt_log.appendPlainText("Cancelando download...")
            self.process.kill()
        elif self.analysis_process is not None:
            self.txt_log.appendPlainText("Cancelando análise...")
            self.analysis_process.kill()

    def set_running_state(self, running):
        self.btn_baixar.setEnabled(not running)
        self.btn_analisar.setEnabled(not running)
        self.btn_procurar.setEnabled(not running)
        self.btn_limpar.setEnabled(not running)
        self.btn_cancelar.setEnabled(running)
        self.btn_marcar_todos.setEnabled(not running)
        self.btn_desmarcar_todos.setEnabled(not running)
        self.input_url.setEnabled(not running)
        self.input_nome_arquivo.setEnabled(not running)
        self.input_pasta.setEnabled(not running)
        self.combo_tipo.setEnabled(not running)
        self.combo_qualidade.setEnabled(not running)
        self.check_playlist.setEnabled(not running)
        self.check_embed_thumb.setEnabled(not running)
        self.input_filtro.setEnabled(not running)
        self.table_playlist.setEnabled(not running)
        if not running:
            self.verificar_dependencias()

    def limpar_tudo(self):
        if self.process is not None or self.analysis_process is not None:
            QMessageBox.warning(self, "Aguarde", "Não é possível limpar durante execução.")
            return
        self.input_url.clear()
        self.input_nome_arquivo.clear()
        self.input_pasta.clear()
        self.input_filtro.clear()
        self.check_playlist.setChecked(False)
        self.check_embed_thumb.setChecked(True)
        self.combo_tipo.setCurrentText("Vídeo")
        self.playlist_entries = []
        self.table_playlist.blockSignals(True)
        self.table_playlist.setRowCount(0)
        self.table_playlist.blockSignals(False)
        self.txt_comando.clear()
        self.txt_log.clear()
        self.progress_bar.setValue(0)
        self.lbl_playlist_status.setText("Nenhuma playlist analisada.")
        self.lbl_qtd_itens.setText("0 itens")
        self.sync_ui_state()
        self.reflow_action_buttons()

    @staticmethod
    def format_duration(seconds):
        if not seconds:
            return "--:--"
        try:
            seconds = int(seconds)
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
        except Exception:
            return "--:--"


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(20, 24, 36))
    palette.setColor(QPalette.WindowText, QColor(231, 236, 243))
    palette.setColor(QPalette.Base, QColor(17, 23, 34))
    palette.setColor(QPalette.AlternateBase, QColor(22, 29, 43))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(231, 236, 243))
    palette.setColor(QPalette.Button, QColor(36, 49, 69))
    palette.setColor(QPalette.ButtonText, QColor(231, 236, 243))
    palette.setColor(QPalette.Highlight, QColor(38, 68, 111))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

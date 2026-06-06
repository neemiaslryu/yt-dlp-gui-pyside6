## 📍 Acesso rápido

- [Instalação Windows](#-instalação-no-windows-1)
- [Uso básico](#%EF%B8%8F-uso-básico)


## 🪟 Instalação no Windows
...


# 🎬 YT-DLP GUI

Interface gráfica em **Python + PySide6** para facilitar o uso do `yt-dlp` sem depender do terminal. 🚀
- SIM, Processo  foi feito usando IA, sim. para sanar um problema pessoal. que não achei para minha distro.
 Apesar de ter testado, ainda esta em processo de estudo. 
<img width="1409" height="884" alt="image" src="https://github.com/user-attachments/assets/b46c6a97-95c5-4527-95eb-bb7548037935" />


## ✨ Apresentação

O projeto transforma o uso do `yt-dlp` em uma experiência visual mais simples e organizada. Com ele, você pode baixar vídeos, extrair áudio em MP3, analisar playlists, selecionar itens específicos e acompanhar a execução em tempo real.

## 🛠️ Instalação

### Requisitos

- Python 3.10+
- `yt-dlp`
- `ffmpeg`
- PySide6

### Instalar dependências

```bash
pip install PySide6 yt-dlp
```

### Instalar o ffmpeg

No Debian/Ubuntu:

```bash
sudo apt install ffmpeg
```

No Arch Linux:

```bash
sudo pacman -S ffmpeg
```

## 🪟 Instalação no Windows

### 1. Instale o Python

Baixe e instale o **Python 3.10+** no Windows. Durante a instalação, marque a opção **Add Python to PATH**. Depois confirme no Prompt de Comando:

```bash
python --version
```

### 2. Instale o projeto e as dependências

Abra o **PowerShell** ou o **Prompt de Comando** na pasta do projeto e execute:

```bash
python -m pip install --upgrade pip
python -m pip install PySide6 yt-dlp
```

### 3. Instale o ffmpeg

Baixe o FFmpeg para Windows, extraia o conteúdo e localize a pasta `bin`. Você precisa garantir que `ffmpeg.exe` e `ffprobe.exe` estejam disponíveis.

## ▶️ Uso básico

1. Abra a aplicação.
2. Cole a URL do vídeo ou da playlist.
3. Escolha o tipo de saída: vídeo ou MP3.
4. Se quiser, defina a qualidade e o nome do arquivo.
5. Escolha a pasta de destino.
6. Clique em **Analisar playlist** se a URL tiver vários itens.
7. Marque os itens que deseja baixar.
8. Clique em **Baixar**.


## Menu de Ações 
<img width="421" height="199" alt="image" src="https://github.com/user-attachments/assets/30a3bbd8-0562-4d3a-93ce-adb8798d1208" />

## 🔘 Função dos botões

### 📁 Procurar
Abre a janela para selecionar a pasta de destino onde os arquivos serão salvos.

### 🔎 Analisar playlist
Faz a leitura da playlist informada na URL e carrega os itens na tabela da interface.

### ✅ Marcar todos
Seleciona todos os itens visíveis da playlist para download.

### ⬜ Desmarcar todos
Remove a seleção de todos os itens visíveis da playlist.

### ⬇️ Baixar
Inicia o download usando as opções configuradas na interface.

### 🛑 Cancelar
Interrompe a análise ou o download que estiver em execução.

### 🧹 Limpar
Remove os dados preenchidos, a lista da playlist, o log e o preview do comando, retornando a interface ao estado inicial.

### Executar o programa

```bash
python MAIN.py
```






## 📌 Observações

- Para converter em MP3, o `ffmpeg` precisa estar instalado.
- O comando final gerado aparece na interface antes da execução.
- Logs e progresso são exibidos durante o processo.

# 🌍 Language Translation Tool

An AI-powered language translation tool with text-to-speech capabilities built with Python, Streamlit, and modern translation APIs.

## ✨ Features

- 🔤 Translate text between 50+ languages
- 🎯 Auto-detect source language
- 🔊 Text-to-speech for translated text
- 📋 Copy translated text to clipboard
- ⚡ Fast and responsive UI
- 🔄 Language swap functionality
- 📊 Translation history
- 🎨 Clean, intuitive interface

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/language-translation-tool.git
cd language-translation-tool
```

2. Install UV (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Copy environment variables:
```bash
cp .env.example .env
```

5. Run the application:
```bash
streamlit run src/app.py
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Translation**: Google Translate API, Deep Translator
- **Text-to-Speech**: gTTS, pyttsx3
- **HTTP Client**: httpx
- **Package Manager**: UV

## 📁 Project Structure
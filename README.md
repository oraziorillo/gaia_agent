# Gaia Agent - AI-Powered Question Answering System

## 🎯 Project Purpose

This project implements an AI agent that can answer questions using multiple tools and capabilities. The Gaia Agent is built with a ReAct (Reasoning and Acting) architecture that leverages OpenAI's API to process questions and utilize various tools including:

- **Web Search**: Real-time information retrieval from the web
- **Wikipedia Integration**: Access to Wikipedia pages and content
- **Calculator**: Mathematical expression evaluation
- **YouTube Video Analysis**: Content analysis of YouTube videos using Google's Gemini API

The system is designed to provide accurate, well-reasoned answers by combining multiple information sources and tools in an intelligent manner.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Google API key (for YouTube analysis)

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Final_Assignment_Template
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root with the following variables:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## 📖 Usage

### CLI Utility (run.py)

The main interface for interacting with the Gaia Agent is through the `run.py` CLI utility:

#### Basic Usage
```bash
python run.py -q "Your question here" -f path/to/file
```

#### Command Line Options
- `-q, --question`: The question for the agent (required)
- `-f, --file`: Path to an input file (optional)
- `-m, --openai-model`: OpenAI model to use (default: gpt-4.1-mini)
- `-v, --verbose`: Show extra debugging information
- `-h, --help`: Show help message

#### Examples

**Simple question:**
```bash
python run.py -q "What is the capital of France?"
```

**Question with file input:**
```bash
python run.py -q "Summarize this document" -f document.txt
```

**Using a specific model:**
```bash
python run.py -q "Calculate 2+2" -m gpt-4.1-mini
```

**Verbose mode for debugging:**
```bash
python run.py -q "What's the weather like?" -v
```

### Supported File Types

The agent can process various file types:

- **Images**: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif` (vision processing)
- **Audio**: `.mp3`, `.wav`, `.m4a` (transcription)
- **Documents**: `.py`, `.xlsx`, `.csv` (code interpretation)

## 🛠️ Project Structure

```
Final_Assignment_Template/
├── agent.py              # Main agent implementation
├── app.py                # Gradio web interface for Hugging Face Spaces
├── run.py                # CLI utility
├── requirements.txt      # Python dependencies
├── settings.py          # Configuration settings
├── utils.py             # Utility functions
└── tools/               # Tool implementations
    ├── __init__.py
    ├── calculator.py
    ├── web_search.py
    ├── wikipedia_retrieval.py
    └── youtube_video_analysis.py
```

## 🌐 Web Interface (app.py)

The `app.py` file is specifically designed for deployment on Hugging Face Spaces. It provides a Gradio web interface that allows users to:

1. Log in with their Hugging Face account
2. Run evaluations on predefined question sets
3. Submit answers for scoring
4. View results and performance metrics

This interface is used for the final assignment submission and evaluation process.

### Currently Available Tools

- **`evaluate_expression`**: Mathematical calculations
- **`wikipedia_page_search`**: Wikipedia page search
- **`wikipedia_page_sections_retriever`**: Get Wikipedia page sections
- **`wikipedia_section_content_retriever`**: Retrieve specific section content
- **`web_search`**: Web search functionality
- **`analyze_youtube_video`**: YouTube video analysis
- **`code_interpreter`**: Run code in a sandbox

## 📝 Notes

- The agent uses a maximum of 10 iterations (by default, but it can be changed) to prevent infinite loops
- File processing supports multiple formats with appropriate strategies
- The system is designed to be extensible with additional tools

## 🚀 Potential Extensions

- Expand the agent's capabilities by implementing additional tools. 
- Introduce a "planning" step before tool execution, where the agent outlines a high-level plan or reasoning steps.
- Improve Error Handling and Logging
- Implement ad-hoc strategies for handling more file types, e.g., PDFs, DOCX, and other common formats.
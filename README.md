# Research-Agent-with-PDF-support
An autonomous AI Research Agent built with LangChain and Streamlit. Supports arXiv search, web retrieval, and local PDF analysis with multilingual Hebrew/English output.


# AI Research Agent for Electrical Engineering

An autonomous Research Assistant built with **LangChain** and **Streamlit**, designed to streamline academic and technical literature reviews. This agent was specifically developed to assist in VLSI and hardware research, but can be applied to any technical domain.

## Key Features
- **Smart Web Search:** Powered by Tavily for real-time technical specs and industry news.
- **Academic Integration:** Directly queries **arXiv** for the latest research papers.
- **Local PDF Analysis (RAG):** Upload your own datasheets or research papers; the agent prioritizes this context in its analysis.
- **Multilingual Output:** Generates professional reports in both **Hebrew (RTL)** and **English**.
- **Gap Analysis:** Identifies research gaps and proposes future research directions.

## Tech Stack
- **Framework:** LangChain
- **LLM:** OpenAI GPT-4o
- **UI:** Streamlit
- **PDF Processing:** PyPDF2
- **Data Fetching:** Tavily API & Arxiv API

## Environment Variables & Security

This project uses environment variables to keep API keys secure.

### Setup
1. Create a `.env` file in the root directory.
2. Add your API keys as follows:
   ```env
   OPENAI_API_KEY=your_openai_key_here
   TAVILY_API_KEY=your_tavily_key_here

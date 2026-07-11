# 🕸️ Knowledge Graph AI Assistant

Query any Neo4j knowledge graph using natural language, or instantly import a sample graph to get started.

## 🚀 Live Demo

👉 **Try the app here:**  
[https://knowledge-graph-ai-assistant-kgfxgojcosst5gjvtvoxfs.streamlit.app/](https://knowledge-graph-ai-assistant-kgfxgojcosst5gjvtvoxfs.streamlit.app/)

---

## ✨ Features

- 🔍 Ask natural language questions over a Neo4j graph
- 🧠 Auto-generates Cypher queries using LLMs (Groq models)
- 📊 Shows detected graph schema
- 🎬 One-click sample dataset import:
  - IMDb Movies
  - Books
- 💬 Multi-conversation support with reset option
- 🛡️ Read-only Cypher generation constraints for safer querying

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/)
- [Neo4j](https://neo4j.com/)
- [LangChain](https://www.langchain.com/)
- [langchain-neo4j](https://python.langchain.com/)
- [Groq](https://groq.com/)

---

## 📦 Installation

```bash
git clone https://github.com/Shuvadip-Dutta/knowledge-graph-ai-assistant.git
cd knowledge-graph-ai-assistant
pip install -r requirements.txt
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

Then open the local URL shown in your terminal (usually `http://localhost:8501`).

---

## 🔑 Requirements

From `requirements.txt`:

- neo4j
- langchain
- langchain_community
- langchain_groq
- python-dotenv
- ipykernel
- langchain-neo4j
- streamlit

---

## 🖼️ Screenshots

<img width="1915" height="867" alt="App Screenshot 1" src="https://github.com/user-attachments/assets/3f038f29-a549-4890-8033-83c7b997057f" />
<img width="1917" height="870" alt="App Screenshot 2" src="https://github.com/user-attachments/assets/9ab9784b-d741-4edd-9a9f-df5cd97c7a3a" />
<img width="1902" height="863" alt="App Screenshot 3" src="https://github.com/user-attachments/assets/29f95c1c-1fa7-4800-ab0b-e43b0e543629" />

---

## 📄 License

Add your preferred license here (e.g., MIT).

# 🚀 ReviewSense – Agentic RAG Chatbot for Amazon Review Intelligence

ReviewSense is an AI-powered **Agentic Retrieval-Augmented Generation (RAG)** system designed to analyze and answer questions about Amazon customer reviews using **semantic search**, **PostgreSQL + pgvector**, **LLM reasoning**, and a **Supervisor Agent** that intelligently selects the best retrieval strategy.

Instead of relying solely on vector search, ReviewSense dynamically decides whether to perform:

- Semantic Retrieval
- SQL Analytics
- Direct Review Lookup
- Statistical Analysis
- Multi-Step Tool-Based Reasoning

This enables highly accurate, context-aware answers grounded in real customer feedback.

---

## 🌟 Key Highlights

- 📊 **21,000+ Amazon Reviews Indexed**
- 🌍 **149+ Countries Covered**
- 🤖 **Agentic AI Architecture**
- 🧠 **Supervisor-Based Tool Selection**
- 🔎 **Semantic Search using pgvector**
- 📈 **SQL-Powered Analytics**
- ⚡ **Groq LLM Integration**
- 🗂️ **Review ID Lookup**
- 🌐 **FastAPI Backend**
- 💬 **Natural Language Query Interface**

---

## 🏗️ System Architecture

```text
                 User Query
                      │
                      ▼
             FastAPI Application
                      │
                      ▼
             Chatbot Orchestrator
                  (chatbot.py)
                      │
                      ▼
               Supervisor Agent
                      │
     ┌────────────────┼────────────────┐
     │                │                │
     ▼                ▼                ▼

Semantic        SQL Analytics      MCP Tools
Retrieval           Tools
     │                │
     ▼                ▼

pgvector        PostgreSQL
Search          Queries

     └────────────────┬────────────────┘
                      │
                      ▼
                  Groq LLM
                      │
                      ▼
                Final Response
```

---

## ✨ Features

### 🤖 Agentic Query Processing

The Supervisor Agent analyzes each query and decides the optimal execution path.

Examples:

| User Query | Strategy |
|------------|-----------|
| What are the main reasons for 1-star reviews? | Semantic Retrieval + LLM Analysis |
| Show me 10 reviews from India | SQL Query |
| What did review 12283 say? | Direct Database Lookup |
| Compare US and UK customer sentiment | SQL + Semantic Analysis |

---

### 🔍 Semantic Search

Uses vector embeddings and pgvector similarity search to retrieve reviews based on meaning rather than keywords.

Example:

```text
Why are customers unhappy with delivery?
```

Retrieves reviews discussing:

- Late deliveries
- Missing packages
- Shipping delays
- Damaged shipments

even if those exact words were not used in the query.

---

### 📊 SQL Analytics

Structured database queries provide:

- Rating distributions
- Country-wise review counts
- Average ratings
- Regional comparisons
- Review statistics

without requiring vector search.

---

### 📝 Direct Review Lookup

Retrieve any review instantly using its unique review ID.

Example:

```text
What did review 12283 say?
```

---

### 🌍 Country-Level Analysis

Analyze customer sentiment and feedback across different regions.

Examples:

```text
Show reviews from India

Compare US and UK ratings

What complaints are common in Germany?
```

---

### 📈 Business Insights

Discover:

- Top complaints
- Product quality issues
- Packaging problems
- Delivery concerns
- Refund trends
- Positive customer feedback

---

## 🛠️ Technology Stack

| Layer | Technology |
|---------|------------|
| Backend API | FastAPI |
| Language | Python |
| Database | PostgreSQL |
| Vector Database | pgvector |
| Embeddings | Sentence Transformers |
| LLM | Groq |
| Agent Layer | Custom Supervisor Agent |
| Retrieval | Semantic Search + SQL Tools |
| Frontend | HTML, CSS, JavaScript |
| Dataset | Amazon Reviews Dataset |

---

## 📂 Project Structure

```text
ReviewSense/
│
├── app.py
├── chatbot.py
├── ingest.py
├── index.html
├── README.md
├── requirements.txt
├── setup_database.sql
│
├── data/
│   └── Amazon_Reviews.csv
│
└── services/
    ├── database.py
    ├── embeddings.py
    ├── llm.py
    ├── mcp_tools.py
    ├── retriever.py
    ├── sql_tools.py
    ├── supervisor.py
    └── router.py.bak
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/ReviewSense.git

cd ReviewSense
```

---

### 2. Create Virtual Environment

```bash
python -m venv ragenv
```

Activate environment:

#### macOS / Linux

```bash
source ragenv/bin/activate
```

#### Windows

```bash
ragenv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reviews_db
DB_USER=postgres
DB_PASSWORD=your_password

GROQ_API_KEY=your_groq_api_key
```

---

### 5. Setup Database

Create PostgreSQL database and run:

```bash
psql -U postgres -d reviews_db -f setup_database.sql
```

---

### 6. Ingest Dataset

```bash
python ingest.py
```

This will:

- Load CSV data
- Generate embeddings
- Store reviews in PostgreSQL
- Create vector embeddings for semantic retrieval

---

### 7. Run Application

```bash
uvicorn app:app --reload
```

Application URL:

```text
http://localhost:8000
```

API Documentation:

```text
http://localhost:8000/docs
```

---

## 📚 Example Queries

### Review Analysis

```text
What are the top customer complaints?
```

```text
Why are users giving 1-star ratings?
```

```text
Summarize packaging-related issues.
```

---

### Country Analysis

```text
Show reviews from India.
```

```text
Compare customer sentiment between the US and UK.
```

```text
Which country has the highest average rating?
```

---

### Review Lookup

```text
What did review 12283 say?
```

```text
Show review 8450.
```

---

### Statistics

```text
How many 5-star reviews exist?
```

```text
Give me rating distribution.
```

```text
Show review counts by country.
```

---

## 🚀 Deployment

The application can be deployed on:

- Render
- Railway
- DigitalOcean
- AWS EC2
- Azure App Service
- Google Cloud Run

Recommended setup:

- FastAPI Backend
- PostgreSQL Database
- pgvector Extension
- Groq API Integration

---

## 🔮 Future Improvements

- LangGraph Integration
- Multi-Agent Architecture
- Sentiment Analysis Dashboard
- Review Trend Visualization
- Streaming Responses
- Authentication & User Sessions
- Review Summarization Reports
- Advanced Analytics Dashboard

---

## 👨‍💻 Author

**Adarsh Bhagat**

AI/ML Engineer

---

## 📄 License

This project is licensed under the MIT License.

Feel free to use, modify, and distribute this project.
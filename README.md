# 📊 Donna Business Agent

**Donna** is an **AI-powered business assistant** that automates routine tasks like email handling, calendar scheduling, and team collaboration. It also intelligently analyzes business documents such as PDFs, Excel files, and CSVs. With a powerful chatbot interface, Donna integrates seamlessly with **Microsoft Graph API**, **Azure OpenAI**, **PandasAI**, and more.

---

## 🧠 Key Features

- 🤖 **Conversational AI** – Chatbot interface powered by LLMs (Azure OpenAI)
- 📄 **Smart Document Processing** – Analyze PDFs, Excel, and CSVs using AI
- 📧 **Business Task Automation** – Manage emails, calendars, Teams messages
- ☁️ **Integrated Tools** – Leverages Microsoft Graph API & Azure Document Intelligence
- 📈 **AI Data Analysis** – Uses PandasAI to handle data-centric queries and visualizations

---

## 🛠️ Tech Stack

- **FastAPI**
- **Azure OpenAI** (LLMs)
- **PandasAI**
- **Azure Document Intelligence**
- **Microsoft Graph API**

---




# 🧩 Key Modules

## 1. Workflow Management Module  
**Natural Language Chatbot UI**

Handles:

- 📅 Tasks & Events  
- 📧 Emails  
- 📇 Contacts  
- 🧑 Users  
- 💬 Microsoft Teams  

Powered by:  
**Microsoft Graph API + Tavily Search API**

#### 🧠 Step-by-Step Explanation

1. **User Input**  
   The user types a natural language prompt, such as:  
   - “Schedule a meeting with Alex next week”  
   - “What’s the latest update on Tesla from the web?”

2. **NLP via LLM (Azure OpenAI)**  
   The AI processes the input to:
   - Understand the intent  
   - Extract parameters like names, dates, actions  
   - Detect if any required details are missing

3. **Check for Missing Parameters**  
   - ✅ If complete: proceed to the appropriate API  
   - ❌ If incomplete: ask the user for missing info  
     e.g., “What time should I schedule the meeting with Alex?”

4. **Call Appropriate Tool/API**  
   - 📧 For email, calendar, Teams → Use **Microsoft Graph API**  
   - 🔍 For real-time web info → Use **Tavily Search API**

5. **Return Output to User**  
   The system responds naturally, e.g.:  
   - “Meeting with Alex scheduled for Tuesday at 2 PM.”  
   - “Here’s the latest news on Tesla: [summary]”

![Workflow Management Diagram](2.png)

---

## 2. Document Analyzer Module  

### 📝 Description
This module enables users to upload documents (PDF, Excel, CSV) and interact with their content using natural language. Users can ask questions, extract insights, and even generate graphs—all through a conversational interface.

---


### 🔁 Workflow Flowchart

#### A) 📄 **For PDF Files**  
- PandasAI loads the spreadsheet into memory and interprets questions like:  
  *“Show sales trends over the last 6 months”*  
- The system can respond with:
  - Plain answers (e.g., summaries, totals)
  - Dynamic charts (bar, line, pie) based on the file contents

---

### ✅ Example Use Cases

- Summarizing financial reports in PDFs  
- Generating trend graphs from Excel sales data  
- Finding anomalies or totals in large CSV files


### 🛠️ Technologies Used

- **Azure Document Intelligence** → For structured PDF extraction and parsing  
- **PandasAI + LLM (GPT-4)** → For querying and analyzing Excel/CSV files  
- **Azure AI Foundry** → Integrates GPT-4 capabilities into the analysis pipeline  

---

![Document Analyzer Diagram](1.png)

---

## 📚 Features

- 🔍 Web Search via Tavily API  
- 🧠 NLP via Azure OpenAI (GPT-4)  
- ✅ Intelligent parameter extraction and feedback loop  
- 📊 Analyze Excel files and generate graphs in seconds  
- 📄 Summarize PDFs using AI  
- ✉️ Send emails by simply giving a prompt  
- 📅 Manage meetings by checking participants' availability  



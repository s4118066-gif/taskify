# Taskify Guide Agent - APAC Hackathon 2026

Taskify is an AI-powered Executive Assistant built using the **Google ADK (Agent Development Kit)** and **Vertex AI**. It allows users to manage their workspace effectively by interacting with Google Cloud Datastore through natural language.

## 🚀 Features
- **Task Management**: Add, list, and mark tasks as complete.
- **Persistent Notes**: Save and retrieve important information/notes.
- **Multi-Agent Orchestration**: Uses a routing agent and a specialized coordinator to handle complex user requests.
- **Generative Summaries**: Formats database outputs into human-readable summaries.

## 🛠️ Tech Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **AI Orchestration**: Google ADK / MCP (Model Context Protocol)
- **Database**: Google Cloud Datastore (NoSQL)
- **Deployment**: Google Cloud Run

## 📋 Prerequisites
Before running, ensure you have the following:
1. A Google Cloud Project with **Datastore Mode** enabled.
2. Google Cloud SDK installed and authenticated.
3. Python 3.10 installed locally or using Cloud Shell.

1.Technologies / Google Services Used
​Google Cloud Run: Scalable serverless deployment.
​Google Cloud Build: CI/CD and automated deployment.
​Google Artifact Registry: Container image storage.
​Google Cloud Logging & Monitoring: Observability.
​Google IAM: Access control and security.
​FastAPI: Backend API framework.
​Python: Core application logic.
​2. Why this AI stack & system design?
​FastAPI provides high performance and async support.
​LLM APIs enable natural language \rightarrow action execution.
​Container-based deployment ensures portability.
​Modular architecture allows adding new tools easily.
​3. How it supports scalability & real-world deployment
​Cloud Run auto-scales based on traffic.
​Stateless backend enables horizontal scaling.
​Containerization ensures consistent deployments.
​Cloud monitoring improves reliability.

Core Capabilities
​Question answering capability: Ability to handle user queries.
​Natural language interaction: Conversational interface for ease of use.
​Task management and tracking: Keeping tabs on user goals and progress.
​Smart reminders and scheduling: Intelligent time management.
​Automation & Data
​Real-time API data integration: Fetching live information from external sources.
​Workflow automation: Reducing manual effort through automated steps.
​Data retrieval and organization: Efficiently finding and structuring information.
Technical Infrastructure
​Simple web-based user interface: Accessible front-end for users.
​FastAPI backend for performance: High-speed, modern Python framework.
​Cloud deployment for scalability: Ensures the app can handle growth.


​IAM + secure APIs support production-grade security.


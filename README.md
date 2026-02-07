# 🩺 Personal Health Coach – AI Agents
**HPE GenAI for GenZ Challenge Submission**

## 📌 Overview
Personal Health Coach is an AI-agent–based health monitoring system designed to efficiently compress medical history and wellness data and deliver personalized health recommendations with lower computational cost.

The project focuses on intelligent context compression, allowing AI agents to reason over summarized health data instead of repeatedly processing raw inputs—making the system scalable, fast, and cost-efficient.

## 🎯 Challenge Alignment (HPE GenAI for GenZ)
This project aligns with the challenge goals by:
* Applying Generative AI & AI Agents
* Solving a real-world healthcare scalability problem
* Optimizing processing cost and efficiency
* Demonstrating progressive development via GitHub tracking

## 🧠 Problem Statement
Users generate large volumes of health data including medical history, lifestyle habits, vitals, and wellness logs. Reprocessing this data repeatedly for recommendations is inefficient and expensive.

**The challenge:** How can we retain meaningful health context while reducing computation and inference cost?

## 💡 Solution Approach
We propose a multi-agent Personal Health Coach that:
1. Compresses long-term health data into structured summaries
2. Stores health context as lightweight memory
3. Uses AI agents to generate personalized recommendations
4. Avoids redundant processing of raw historical data

## 🤖 AI Agents Architecture

### 1️⃣ Health Data Compression Agent
* Summarizes medical history, lifestyle patterns, and wellness logs
* Converts raw data into concise structured memory

### 2️⃣ Context Manager Agent
* Maintains rolling health summaries
* Updates compressed memory incrementally

### 3️⃣ Recommendation Agent
* Generates personalized diet, exercise, sleep, and wellness suggestions
* Operates only on compressed context (low-cost inference)

## 🏗️ System Workflow
1. User provides health data (manual or simulated input)
2. Compression Agent summarizes data
3. Context Manager stores optimized health memory
4. Recommendation Agent generates insights
5. System updates memory instead of reprocessing history

## 🧪 Tech Stack
* **Language:** Python
* **AI / GenAI:** LLMs, Prompt Engineering, Summarization
* **Architecture:** Agent-based design
* **Storage:** Lightweight structured summaries (JSON / embeddings)
* **Version Control:** GitHub (progress tracking)

## 📁 Project Structure

```
Personal-Health-Coach/
│
├── agents/
│   ├── compression_agent.py
│   ├── context_manager.py
│   └── recommendation_agent.py
│
├── data/
│   ├── sample_health_data.json
│   └── compressed_memory.json
│
├── prompts/
│   └── agent_prompts.md
│
├── main.py
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* Virtual environment (recommended)

### Setup

```bash
git clone https://github.com/your-username/Personal-Health-Coach.git
cd Personal-Health-Coach
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

## 📊 Progress Tracking (Challenge Requirement)
Development progress is tracked via:
* Incremental commits
* Feature-wise agent implementation
* Documentation updates
* Architecture refinements

Each milestone is pushed to GitHub to demonstrate learning and iteration during the challenge timeline.

## 🌱 Future Enhancements
* Integration with wearable data (steps, sleep, heart rate)
* Real-time health alerts
* Secure medical record handling
* Multi-language health recommendations
* Dashboard for health trends visualization

## 🏁 Conclusion
This project demonstrates how **AI Agents + GenAI** can be used to build efficient, scalable healthcare solutions by intelligently compressing context and minimizing processing costs—aligning strongly with the vision of HPE GenAI for GenZ.

## 👤 Author
**Animesh Sharma**  
HPE GenAI for GenZ Participant

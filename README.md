# 🧠 Smart Follow-Up Assistant

An Agentic AI Mini Project built with LangChain, Gemini, MongoDB, and Streamlit

---

## 🚀 Overview

Smart Follow-Up Assistant is an AI-powered agent that helps you manage follow-ups, reminders, and communication tracking automatically. It uses Google Gemini via LangChain to reason over your messages and decide whether to create a new ticket or append to an existing one in MongoDB.

The project demonstrates agentic reasoning, autonomous decision-making, and context management using modern AI frameworks.

---

## 🧩 Features

- ✅ Understands user intent and creates or updates follow-up tickets
- ✅ Uses Gemini 2.5 Flash model for smart reasoning
- ✅ MongoDB for persistent storage of follow-ups
- ✅ Streamlit UI – clean, fast, and local web dashboard
- ✅ Fully containerized with Docker Compose

---

## ⚙️ Project Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Meet57/FollowUp.git
cd FollowUp
```

### 2️⃣ Create a virtual environment

```bash
# on macOS/Linux
python3 -m venv venv
source venv/bin/activate

# on Windows
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup .env file

Create a `.env` file in the root of the project with the following:

```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# MongoDB Configuration
MONGO_URI=mongodb://root:password@localhost:27017/
MONGO_DB=followupDB
```

### 5️⃣ Run MongoDB with Docker

A ready-to-use `docker-compose.yml` is provided:

```yaml
version: "3.8"
services:
  mongodb:
    image: mongo:latest
    container_name: mongodb
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - ./mongo-data:/data/db

volumes:
  mongo-data:
    driver: local
```

Start MongoDB:

```bash
docker-compose up -d
```

### 6️⃣ Run the Smart Follow-Up Assistant

```bash
streamlit run app.py
```

---

## 🧠 How It Works

### ⚙️ Architecture

```
User Message
     ↓
  Streamlit Chat UI
     ↓
 process_message()
     ↓
  LangChain Agent (Gemini 2.5 Flash)
     ↓
  ├── AddTicket tool → Creates a new ticket in MongoDB
  └── AppendMessage tool → Adds message to an existing ticket
     ↓
  MongoDB (Persistent Storage)
```

---

## 💬 Example Flow

**Input:**

```
User: Please send the final report to the client by Friday.
```

**AI Agent Decision:**

```json
{
  "tool": "AddTicket",
  "args": {
    "type": "task",
    "title": "Send final client report",
    "description": "The user requested to send the final report to the client by Friday.",
    "action": "Send the final report to the client before Friday.",
    "messages": ["Please send the final report to the client by Friday."]
  }
}
```

**Result:**

✅ A new follow-up ticket is added to MongoDB.

---

## 🧱 Project Structure

```
📦 Smart-FollowUp-Assistant
│
├── agent.py                # AI Agent logic (LangChain + Gemini)
├── db.py                   # MongoDB CRUD operations
├── app.py                  # Streamlit frontend
├── docker-compose.yml      # MongoDB container setup
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
└── README.md               # This file
```

---

## 🧪 Testing

Try sending a few messages through the Streamlit UI:

| Example Message                          | Expected Action                     |
| ---------------------------------------- | ----------------------------------- |
| "Send the report by Monday."             | Creates new ticket                  |
| "Any updates on the report?"             | Appends to previous report ticket   |
| "Set a reminder for tomorrow's meeting." | Creates new reminder ticket         |
| "CTO said project is completed."         | Updates the relevant project ticket |

---

## 🧠 Reflection

**What worked well:**

- Seamless integration of Gemini via LangChain tools
- Auto-detection of related vs new tickets
- MongoDB persistence and Streamlit simplicity

**What can be improved:**

- Add scheduling/notification system (e.g., cron or schedule module)
- Integrate with Gmail/Slack for real-world follow-ups
- Add embeddings for better semantic matching between messages

---

## 🧰 Tech Stack

| Component     | Technology                   |
| ------------- | ---------------------------- |
| Frontend      | Streamlit                    |
| Backend/Agent | LangChain + Gemini 2.5 Flash |
| Database      | MongoDB (Docker)             |
| Language      | Python 3.9+                  |
| Environment   | .env for API Keys & Configs  |

---

## 💡 License

MIT License © 2025 [Meet Patel]

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Meet57/FollowUp/issues).

## 📧 Contact

Meet Patel - [@Meet57](https://github.com/Meet57)

Project Link: [https://github.com/Meet57/FollowUp](https://github.com/Meet57/FollowUp)
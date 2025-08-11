# 🌱E-Mealio + PHaSE: A Chat Agent for Sustainable and Healthy Recipes Suggestions

A project originally developed by **Antonio Raffaele Iacovazzi** as part of his *Master’s Thesis in Computer Science*, with the goal of developing a chat-based agent that helps users adopt sustainable food habits.

Subsequently, **Lorenzo Blanco**, as part of his *Bachelor's Thesis in Computer Science*, further developed the chat-based agent by enhancing its functionalities, improving usability and overall user experience, and expanding its domain beyond sustainability to also address the promotion of healthy food habits.

This new version leverages [PHaSE](https://github.com/tail-unica/PHaSEAPI) APIs as main source of information and recommendations.

---

## 🔌 Current Status

**✅ Bot Status: ONLINE**  
The Telegram bot is currently **active and operational**. You can interact with it searching **@emealio_phase_bot** on Telegam and typing the `/start` command.

---
## 🐳 How to Run it with Docker

You can easily run E-Mealio + PHaSE fully containerized with Docker and Docker Compose — no manual setup required.

### ✅ Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PHaSE API](https://github.com/tail-unica/PHaSEAPI)
### 📁 Project Structure (Relevant Files)

```
PHaSEAPI/
└── ...
PHaSEAPI-integration-in-E-Mealio/
├── docker-compose.yml
├── Dockerfile
├── mongo_dump/                  # Precomputed MongoDB dump (BSON format), WARNING: the actual files are not in the folder, check the readme inside to understand how to download them. 
├── .env                         # Contains API keys
└── projectRoot/                 # Main bot code
```

IMPORTANT: PHaSEAPI and PHaSEAPI-integration-in-E-Mealio (the current project) must lay in the same folder.
---

### 🔑 1. Set Environment Variables

Create a `.env` file in the root (same directory as `docker-compose.yml`) with:

```env
OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ANTHROPIC_API_KEY=your_anthropic_key
```

> You can leave some variables blank if you're not using a specific provider.

---

### 🚀 2. Build and Launch the Containers

From the root of the project, run:

```bash
docker-compose up --build
```

This will:

- Start a MongoDB container
- Automatically restore the precomputed database from `/mongo_dump`
- Launch the Telegram bot

---

### 🧪 3. Verify It’s Working

- Open your Telegram bot and send `/start`
- You should receive a response from the bot within a few seconds 🎉

---

### 💾 MongoDB Persistence

MongoDB data is stored in a Docker-managed volume named `mongo_data`.

To **completely reset** the environment (including clearing the database), run:

```bash
docker-compose down -v
```

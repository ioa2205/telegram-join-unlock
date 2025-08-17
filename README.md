# Telegram Join-to-Unlock Bot


A production-ready Telegram bot designed for marketing funnels. Users arrive via a deep-link (`t.me/YourBot?start=slug`), must join a designated channel or group to verify their membership, and are then granted access to a single, specific file associated with that link.

This project features a fully interactive, stats-driven admin panel, a robust backend using PostgreSQL, and a professional webhook-based deployment strategy.

---

## ✨ Features

-   **Deep-Link Funnel:** Each user is locked into a single-offer funnel based on the unique `slug` they start the bot with.
-   **Forced Subscription Gate:** Users must join a verification channel/group to unlock the promised content. Membership is re-verified before every file delivery.
-   **Efficient File Delivery:** Utilizes Telegram's `file_id` system to send files instantly without re-uploading.
-   **Powerful Admin Panel (`/admin`):**
    -   **At-a-Glance Dashboard:** View key stats like total users and conversion rates directly in the main panel.
    -   **Interactive Slug Management:** A paginated, button-based interface to view, add, and delete slugs.
    -   **Data-Driven Insights:** View performance metrics (starts, verifications, file sends, conversion rate) for each individual slug.
    -   **Guided Wizards:** Foolproof, step-by-step conversational flows (FSM) for adding new slugs and broadcasting messages.
    -   **Safe Broadcasting:** Includes a preview and confirmation step to prevent accidental broadcasts to all users.
-   **Scalable Backend:**
    -   **PostgreSQL Database:** A robust, production-grade database to handle high user loads.
    -   **Webhook-Ready:** Built to run on efficient, instant webhooks (can also run in polling mode for simple testing).
-   **Polished User Experience:**
    -   Personalized welcome messages.
    -   Clear, helpful instructions and error messages.

---

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   Python 3.11+
-   [Docker](https://www.docker.com/products/docker-desktop/) installed and running (for the PostgreSQL database).
-   A Telegram Bot Token from [@BotFather](https://t.me/BotFather).
-   A verification channel/group where your bot is an administrator.

### ⚙️ Installation & Setup (Local)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ioa2205/telegram-join-unlock.git
    cd your-repo-name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Copy the example file and fill in your credentials.
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file with your own values for the bot token, admin IDs, channel info, and database credentials. The default database values match the `docker-compose.yml` file.

5.  **Start the PostgreSQL Database:**
    In your terminal, run the following command. This will start the database server in the background.
    ```bash
    docker-compose up -d
    ```

6.  **Run the Bot (Polling Mode):**
    For simple local testing, ensure `USE_WEBHOOK=false` in your `.env` file and run the main script:
    ```bash
    python main.py
    ```
    The bot is now running!

### 🧪 Testing with Webhooks (Optional, Local)

To test the production-ready webhook functionality on your local machine:

1.  **Install [ngrok](https://ngrok.com/download)** and configure your authtoken.

2.  **Start ngrok** to create a public tunnel to your bot's local web server:
    ```bash
    ngrok http 8080
    ```

3.  **Update your `.env` file:**
    -   Set `USE_WEBHOOK=true`.
    -   Copy the `https://....ngrok-free.app` URL from your ngrok terminal and paste it as the value for `BASE_WEBHOOK_URL`.

4.  **Run the Bot:**
    ```bash
    python main.py
    ```
    The bot will start in webhook mode and register its URL with Telegram.

---

## 🔧 Usage

### For Users

-   Start the bot with a unique deep-link: `https://t.me/<YourBotUsername>?start=<slug_name>`
-   Follow the on-screen instructions to join the channel and verify.
-   Receive the file.

### For Admins

-   `/admin`: The primary entry point to the interactive control panel. From here, you can manage slugs and send broadcasts.
-   `/stats`: A quick command to view overall bot statistics.

---

## 🚢 Deployment

A detailed guide for deploying this bot to a production server (e.g., a VPS from Hetzner or DigitalOcean) can be provided. The general steps are:

1.  Set up a clean Ubuntu 22.04 server.
2.  Install Docker and Docker Compose.
3.  Copy the project files to the server.
4.  Run the PostgreSQL database via `docker-compose`.
5.  Configure a reverse proxy like **Nginx** for security and performance.
6.  Obtain a free SSL certificate from **Let's Encrypt**.
7.  Create a **`systemd`** service to run the `python main.py` script continuously and ensure it restarts on failure or server reboot.

---

## 🛠️ Built With

-   [Python 3.11](https://www.python.org/)
-   [aiogram 3.x](https://github.com/aiogram/aiogram) - The best asynchronous Telegram Bot API framework.
-   [PostgreSQL](https://www.postgresql.org/) - The world's most advanced open source relational database.
-   [Docker](https://www.docker.com/) - For containerized, reproducible environments.
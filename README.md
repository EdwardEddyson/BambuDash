# BambuDash

BambuDash is a self-hosted management system for Bambu Lab 3D printers, designed for cost tracking, filament management, and multi-user environments.

## ✨ Features

- **Filament Management**: Track spool usage, cost, material type, and color. Integrates with Bambu AMS via MQTT for real-time data.
- **Project & Print Job Tracking**: Organize your 3D models and track their print history and filament consumption.
- **Order Management**: Manage filament orders and automatically calculate costs.
- **Split-Billing**: Easily split the cost of filament spools among multiple users, perfect for shared printers in a lab or makerspace.
- **Dockerized**: Simple, one-command deployment using Docker and Docker Compose.
- **Portainer Ready**: Deploy and manage the application easily through Portainer's Git Stacks.

## 🛠️ Technology Stack

- **Backend**: Python 3.12 with [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: PostgreSQL
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/)
- **Real-time**: MQTT for printer communication
- **Deployment**: Docker & Docker Compose
- **Frontend**: Next.js (Planned)

## 🚀 Getting Started

There are two ways to get BambuDash running: via Portainer (recommended for servers) or locally for development.

### Prerequisites

- Git
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Method 1: Deploying with Portainer (Recommended)

This is the easiest way to run BambuDash on a server.

1.  **Add Project to Git**: Make sure this project is on a Git provider like GitHub or GitLab.
2.  **Create Portainer Stack**:
    - In Portainer, go to **Stacks** > **+ Add stack**.
    - Select **Git Repository** as the build method.
    - **Name**: Give the stack a name (e.g., `bambudash`).
    - **Repository URL**: Enter the URL of your Git repository.
    - **Compose path**: Ensure this is set to `docker-compose.yml`.
    - If your repository is private, enable **Authentication** and provide credentials.
3.  **Upload Environment File**:
    - Under the environment settings in the stack screen, select the **Upload** option or paste your values.
    - Create a local copy of [`.env.example`](file:///c:/Users/Edwar/Documents/dev/BambuDash/.env.example), rename it to `.env`, edit it with your secure credentials, and upload it.
4.  **Deploy**: Click **Deploy the stack**. Portainer will pull the repository, build the backend image, and start both the database and backend services.

To update the application, simply `git push` your new changes and click the **"Pull & redeploy"** button on the stack's detail page in Portainer.

### Method 2: Local Development

1.  **Clone the repository**:
    ```bash
    git clone <your-repository-url>
    cd BambuDash
    ```
2.  **Set up Environment Variables**:
    - Copy the example environment file:
      ```bash
      cp .env.example .env
      ```
    - Open `.env` and adjust the variables (like database password and secrets).
3.  **Start the Database**: Use the provided `docker-compose.yml` to start just the database service.
    ```bash
    docker-compose up -d db
    ```
4.  **Set up Python Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```
5.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
6.  **Run the Backend**:
    ```bash
    uvicorn backend.app.main:app --reload
    ```

## ⚙️ Configuration

Application settings (like database URL, JWT secrets, and MQTT details) are configured via environment variables.

For local development and Docker deployment, copy the [`.env.example`](file:///c:/Users/Edwar/Documents/dev/BambuDash/.env.example) template to a file named `.env` and fill in the values:

- **`POSTGRES_USER` / `POSTGRES_PASSWORD`**: Database credentials. The `DATABASE_URL` is automatically constructed from these variables in [docker-compose.yml](file:///c:/Users/Edwar/Documents/dev/BambuDash/docker-compose.yml).
- **`SECRET_KEY`**: A secure string used to sign JWT access tokens.
- **`MQTT_*`**: Credentials and settings for your local MQTT broker (for direct printer connection).
- **`BAMBU_CLOUD_*`**: Credentials for the Bambu Cloud MQTT API.

## 📚 API Documentation

Once the application is running, the interactive API documentation (powered by Swagger UI) is available at:

[http://localhost:8000/docs](http://localhost:8000/docs)

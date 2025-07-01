
# Startup Hub - Backend

This repository contains the backend service for the Startup Hub platform. It is engineered with a focus on scalability, maintainability, and a non-blocking user experience by leveraging a modern, decoupled architecture.

## Core Architectural Philosophy

The backend is designed as a robust **modular monolith** that orchestrates a suite of specialized **AI microservices**. This approach provides the rapid development speed of a unified Django framework while offering the scalability and resilience of a microservice architecture for its most intensive computational tasks.

## Technology Stack

| Component            | Technology                                        | Purpose                                             |
| -------------------- | ------------------------------------------------- | --------------------------------------------------- |
| **Backend Framework**  | Django, Django Rest Framework (DRF)               | Core application logic, REST API, security          |
| **Database**           | PostgreSQL                                        | Reliable and scalable relational data storage       |
| **Async Task Queue**   | Celery                                            | Executing long-running background jobs            |
| **Message Broker**     | RabbitMQ                                          | Mediating communication between Django & Celery     |
| **Result Backend**     | Redis                                             | Storing task state and results efficiently        |
| **Authentication**     | `dj-rest-auth` (Token-based)                      | Secure, stateless user authentication             |

## System Architecture Diagram

This diagram illustrates the separation of concerns and data flow between the core application, the asynchronous task processing system, and the external AI agents.

![System Architecture](docs/uml/2_component_diagram.png)

## Key Architectural Benefits

### 1. Decoupled AI Microservices
The backend does not perform heavy AI computation itself. Instead, it delegates these tasks to specialized, independent Python (Flask/FastAPI) services.

-   **Benefit: Scalability & Resilience.** AI agents can be scaled independently of the main application based on their specific load. If one agent (e.g., report generation) experiences high traffic or fails, it does not impact the core application or other services like the real-time chatbot.
-   **Benefit: Technology Freedom.** Each agent is a self-contained microservice. This allows them to be updated, optimized, or even rewritten in a different technology (e.g., Go, Node.js) without requiring any changes to the Django monolith.

### 2. Asynchronous Task Processing
For any operation that could take more than a few seconds (e.g., generating a PDF report, calling an AI for a long description), we use a powerful `Celery + RabbitMQ + Redis` stack.

-   **Benefit: Superior User Experience.** The API responds instantly (`202 Accepted`) to the user, confirming that the task has been queued. The user's interface remains fast and responsive, never blocked by a long-running process. The frontend can then poll for the result or receive it via a websocket.
-   **Benefit: Reliability & Resource Management.** This architecture prevents long-running HTTP requests from timing out. It ensures that resource-intensive jobs are processed reliably in the background by a dedicated pool of workers, protecting the web-facing application from being overwhelmed.

### 3. Modular & Secure Core
The main application is built using Django's app-based structure, promoting a clean separation of concerns (`users`, `startups`, `chat`, etc.).

-   **Benefit: High Maintainability & Rapid Development.** This logical separation makes the codebase easy to navigate, test, and extend. The powerful Django ORM and "batteries-included" approach allow for the fast implementation of new features and data models.
-   **Benefit: Security by Design.** By leveraging Django and DRF, we inherit a suite of built-in security features, including protection against common web vulnerabilities (CSRF, XSS, SQL Injection) and a robust permissioning system for the API.

## Local Development Setup

### Prerequisites
-   Python 3.8+
-   PostgreSQL, RabbitMQ, and Redis servers running locally.

### Installation & Configuration

1.  **Clone the repository and enter the directory:**
    ```bash
    git clone <your-repo-url>
    cd startup-hub-backend
    ```

2.  **Set up virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the project root (you can copy from `.env.example`). Fill in your database credentials and ensure the agent URLs are correct.
    ```env
    SECRET_KEY='...'
    DATABASE_URL='postgres://user:password@localhost/startup_hub_db'
    CELERY_BROKER_URL='amqp://guest:guest@localhost:5672//'
    # ... other variables
    ```

4.  **Run Database Migrations:**
    ```bash
    python manage.py migrate
    ```

### Running the System
You must run the following components in separate terminal windows.

1.  **Run the Django Server:**
    ```bash
    python manage.py runserver
    ```

2.  **Run the Celery Worker:**
    ```bash
    celery -A startup_hub worker -l info
    ```

3.  **Run the External AI Agents:**
    Start each AI microservice according to its own instructions.

## API Reference

The system exposes a full REST API for interaction with the frontend. For detailed endpoint documentation, please refer to the Postman collection or an OpenAPI/Swagger specification (if available).




## Visual Architecture (UML Diagrams)

For a detailed visual understanding of the project's architecture, data model, and key interactions, please refer to the UML diagrams below.

### 1. Use Case Diagram
*Shows what different users can do with the system.*
![Use Case Diagram](docs/uml/1_use_case_diagram.png)

### 2. Component Diagram
*A high-level view of the system's software components and their connections.*
![Component Diagram](docs/uml/2_component_diagram.png)

### 3. Class Diagram (Data Model)
*A detailed look at the database schema and model relationships.*
![Class Diagram](docs.uml/3_class_diagram.png)

### 4. Sequence Diagrams
*Step-by-step illustrations of key processes.*

**Asynchronous Report Generation:**
![Sequence Diagram for Report Generation](docs/uml/4a_sequence_report_generation.png)

**Synchronous Chatbot Interaction:**
![Sequence Diagram for Chatbot Interaction](docs/uml/4b_sequence_chatbot_interaction.png)

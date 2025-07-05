# Asset Discovery Service

## Overview

The **Asset Discovery Service** is the first asynchronous worker in the risk assessment pipeline. It acts as a Kafka consumer, listening for `scan.started` events. Upon receiving an event, it performs reconnaissance on the specified domain to identify associated digital assets, such as subdomains and IP addresses.

For each asset found, this service persists the information to the database and publishes a new `asset.discovered` event to Kafka, allowing downstream services (like the Asset Valuation Service) to continue the analysis.

## Tech Stack

- **Language:** Python 3.11+
- **Messaging:** Apache Kafka (kafka-python library)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Reconnaissance Tools:** This service is designed to integrate with various OSINT tools. The initial implementation uses a placeholder, but it can be extended to use tools like `sublist3r`, `amass`, or APIs like Shodan.
- **Containerization:** Docker

## Architecture

This service is a "headless" worker, meaning it has no API endpoints. Its entry point is a long-running consumer process. It follows **Clean Architecture**:

1.  **Domain:** Defines the `Asset` entity, business rules, and abstract repository interfaces (`IAssetRepository`, `IMessagingProducer`).
2.  **Application:** Contains the `DiscoverAssetsUseCase` which orchestrates the asset discovery process.
3.  **Infrastructure:** Provides concrete implementations for repositories (`PostgresAssetRepository`, `KafkaProducer`) and wrappers for external reconnaissance tools (`SubdomainFinder`).
4.  **Worker:** The main process that instantiates the Kafka consumer, listens for messages, and triggers the use case for each message.

## Getting Started

### Prerequisites

- Python 3.11+
- Docker
- PostgreSQL instance
- Apache Kafka instance

### Installation & Running

1.  **Clone, create venv, and install dependencies:**
    ```bash
    git clone <your-repo-url>
    cd asset-discovery-service
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**
    Copy `.env.example` to `.env` and configure your database and Kafka connection details.

3.  **Run the worker:**
    ```bash
    python main.py
    ```
    The service will start listening for messages on the `scan.started` topic. You will see log output in the console.

### Running with Docker

1.  Ensure you have a `.env` file configured.
2.  Build and run the Docker container:
    ```bash
    docker build -t asset-discovery-service .
    docker run --env-file .env asset-discovery-service
    ```
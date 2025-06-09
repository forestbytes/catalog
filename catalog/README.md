# Project Documentation

## Overview
This project is designed to demonstrate the integration of a PostgreSQL database with the pgvector extension for handling vector embeddings. The main application logic is implemented in Python, utilizing the Chroma library for querying collections and managing documents.

## Project Structure
```
catalog
├── src
│   └── main.py          # Main application logic
├── docker
│   └── docker-compose.yml # Docker Compose configuration for PostgreSQL
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed on your machine.

### Running the Project
1. Clone the repository to your local machine.
2. Navigate to the `docker` directory.
3. Run the following command to start the PostgreSQL service:
   ```
   docker-compose up
   ```
4. Ensure that the PostgreSQL database is running and accessible.

### Python Dependencies
To install the required Python packages, run:
```
pip install -r requirements.txt
```

### Usage
- The main application can be executed by running the `src/main.py` file.
- Ensure that the PostgreSQL database is properly configured and running before executing the application.

## License
This project is licensed under the MIT License.
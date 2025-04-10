# catalog  
USFS data catalog tools and projects.  

## Neo4j Overview
This project sets up a Neo4j database using Docker Compose. It provides a simple way to run a Neo4j instance for development and testing purposes.

## Prerequisites
- Docker
- Docker Compose

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd my-neo4j-project
   ```

2. Create a `.env` file based on the provided template:
   ```bash
   cp .env.example .env
   ```

3. Modify the `.env` file to set your database credentials and configuration settings.

4. Start the Neo4j database:
   ```bash
   docker-compose up -d
   ```

5. Access the Neo4j browser at `http://localhost:7474` and log in using the credentials specified in your `.env` file.

## Stopping the Database
To stop the Neo4j database, run:
```bash
docker-compose down
```

## License
This project is licensed under the MIT License.

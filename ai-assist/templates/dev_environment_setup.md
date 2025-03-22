# Development Environment Setup

This template provides instructions for configuring consistent development environments for the project.

## Required Tools

### Core Development Tools

- **Version Control**: Git 2.x+
- **Code Editor**: VS Code [version] with recommended extensions
- **Container Runtime**: Docker [version]
- **Language Runtime**: [Language] [version]
- **Package Manager**: [Package Manager] [version]
- **Database Tools**: [DB Client] [version]

### Language-Specific Tools

#### Python

- Python 3.11+
- uv package manager
- pytest for testing
- Ruff for linting

#### JavaScript/TypeScript

- Node.js [version]
- npm or yarn [version]
- ESLint and Prettier
- Jest for testing

#### Other Languages

[Add tools for other languages used in the project]

## Environment Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
DATABASE_URL=postgresql://[username]:[password]@localhost:5432/[dbname]
API_KEY=development_key
DEBUG=true
LOG_LEVEL=debug
```

> Note: Never commit the `.env` file to version control. A `.env.example` file is provided as a template.

## Local Development

### Docker Compose Setup

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: .docker/Dockerfile.dev
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - .env

  db:
    image: postgres:14
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=app_development

volumes:
  postgres_data:
```

### Virtual Environment Setup

#### Python Virtual Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Node.js Environment

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## Database Setup

### Local Database Configuration

```bash
# Create development database
psql -c "CREATE DATABASE app_development;"

# Run migrations
./manage.py migrate  # Django example
# or
npm run db:migrate  # Node.js example

# Seed database with test data
./manage.py loaddata fixtures/dev_data.json  # Django example
# or
npm run db:seed  # Node.js example
```

### Database Migration Guidelines

- Create migrations for all model changes
- Test migrations both forward and backward
- Document breaking changes

## Running Tests

### Running Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_specific_feature.py
```

### Running Frontend Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- src/components/MyComponent.test.js
```

## Linting and Formatting

### Running Linters

```bash
# Python linting
ruff check .

# JavaScript/TypeScript linting
npm run lint
```

### Running Formatters

```bash
# Python formatting
ruff format .

# JavaScript/TypeScript formatting
npm run format
```

## Environment Customization

### Common Customizations

- Use the `.env` file for environment-specific settings
- Use `.gitignore` to exclude personal customization files
- Document all required environment variables in `.env.example`

### Advanced Configuration

- Create a `local_settings.py` (for Django) or similar for advanced local override
- Document required customizations in this file

## Troubleshooting

### Common Issues

- **Database Connection Issues**: Ensure the database service is running and credentials are correct
- **Port Conflicts**: Check if the required ports are already in use
- **Dependency Issues**: Ensure all dependencies are installed and up to date

### Getting Help

- Check the project documentation in the `docs/` directory
- Consult with team members
- Refer to the project's issue tracker

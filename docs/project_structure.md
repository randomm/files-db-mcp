# Enhanced Project Boilerplate Guidelines for LLM-Assisted Development

## 1. General Setup
- Use clear project structures optimized for LLM understanding:
  - `src/` — source code
  - `tests/` — unit and integration tests
  - `docs/` — documentation
  - `.github/` — GitHub Actions workflows and templates
  - `.docker/` — Dockerfiles if more than one Dockerfile is needed
  - `.tasks/` — project planning files and templates
  - `ai-assist/` — prompts and context files for LLM assistants
  - `docker-compose.yml` and optionally `docker-compose.ci.yml` for CI

## 2. Version Control & Branching Strategy
- Use Git with lowercase commit prefixes: `feat:`, `fix:`, `chore:`, `docs:`, `style:`, `refactor:`, `test:`, `perf:`
- Hybrid GitFlow:
  - `main` branch always deployable
  - Feature branches off `main` using naming convention `feature/ISSUE-ID-short-description`
  - QA testing via force-pushed feature branch deploys
  - Merge into `main` through pull requests with manual review
  - Pull requests must reference the issue ID in the description

## 3. Project Planning & Task Management
- Project planning and task tracking within codebase for LLM assistant comprehension:
  - `.tasks/README.md` - Provides overview of project structure for LLM assistants
  - `.tasks/backlog.md` - Prioritized product backlog items in machine-parsable format
  - `.tasks/sprints/` - Sprint planning and retrospective documentation
  - `.tasks/templates/` - Issue and task templates in markdown
  - `.tasks/ROADMAP.md` - High-level product roadmap

- Issue tracking with LLM-readable formats:
  - Feature requests use `.tasks/templates/feature_request.md` with clear sections
  - Bug reports use `.tasks/templates/bug_report.md` with structured reproduction steps
  - Technical debt items use `.tasks/templates/tech_debt.md` with impact assessment

- Task metadata format for LLM parsing:
  ```md
  --- 
  id: TASK-123
  type: feature|bug|refactor
  priority: high|medium|low
  status: todo|in-progress|review|done
  assignee: github-username
  due: YYYY-MM-DD
  ---
  
  # Task Title
  
  ## Description
  Clear description of the task.
  
  ## Acceptance Criteria
  - [ ] Criteria 1
  - [ ] Criteria 2
  ```

- For complex projects, supplement file-based tracking with:
  - GitHub Projects integration with automation
  - GitHub Issues with custom templates
  - Labels for priority, effort, and type categorization

## 4. LLM-Assisted Development Support
- `ai-assist/` directory containing:
  - `ai-assist/README.md` - Instructions for LLM assistants 
  - `ai-assist/contexts/` - Specialized context files for different development tasks
  - `ai-assist/prompts/` - Reusable prompts for common development tasks
  - `ai-assist/architecture.md` - Simplified architecture overview for LLMs

- Support for Cursor editor and similar tools:
  - `.cursor/settings.json` - Additional Cursor settings
  - `.gitattributes` with LLM-friendly diff settings

- Standardized code comment formats for LLM assistance:
  - `// TODO(TASK-123): Description` - Links task IDs to implementations
  - `// EXPLAIN: Complex logic explanation` - Contextual explanations for LLMs
  - `// CONTEXT: Background information` - Additional context for LLMs

## 5. Python Projects
- Python version: 3.11
- Dependency management: `uv`
- Testing: `pytest` + `pytest-cov`
- Fixtures should be embedded in the codebase, with obfuscated but real test data
- Type hints for all functions to aid LLM comprehension
- Docstrings in Google format for consistent LLM parsing
- Use Black for code formatting, isort for import sorting
- Use Ruff for linting with standardized configuration
- Pre-commit hooks for automated linting and formatting

## 6. Docker & Kubernetes
- Docker images are deployed in Kubernetes using Porter
- Docker Compose setup for local dev and CI with `docker-compose.ci.yml`
- Secrets handled via Kubernetes Secrets managed through Porter UI
- Include health check endpoints in all services
- Document resource requirements in `.docker/resources.md`
- Docker development containers with built-in LLM tools

## 7. React Projects
- Use `__tests__` folders for tests near components
- ESLint for code style enforcement
- Testing with Jest + React Testing Library
- Use styled-components or themes; avoid inline styles
- Implement Storybook for component documentation
- Use Prettier for consistent formatting
- Type safety with TypeScript to assist LLMs
- Component organization with semantically-named directories

## 8. Ruby/Rails Projects
- Rails 7.0, Ruby 3.1.0 as defaults
- Service-oriented design; keep controllers thin and API-focused
- Middleware for subdomain handling where applicable
- Use RSpec for testing with good coverage
- Use Rubocop for style enforcement
- Standard Rails directory structure with added `app/services/` for business logic

## 9. API Design & Documentation
- RESTful API design principles
- OpenAPI/Swagger documentation for all APIs, accessible by LLM assistants
- Versioned API endpoints
- Consistent error response formats
- Rate limiting and authentication standards
- Document API specifications in `docs/api/`

## 10. Code Quality & Standards
- Code review checklist in `.github/PULL_REQUEST_TEMPLATE.md`
- Required approval from at least one team member
- SonarQube or similar static analysis integration
- Defined code coverage thresholds (aim for >80%)
- Consistent naming conventions documented in `docs/coding_standards.md`
- Branch protection rules enforcing tests pass before merge
- LLM-friendly code organization with clear separation of concerns

## 11. Deployment & CI/CD
- Use GitHub Actions workflows for build and deploy pipelines
- CI tests run in `docker-compose.ci.yml` environment
- Deployment environments:
  - `dev` - automatic deployment from `main`
  - `staging` - manual promotion from `dev`
  - `production` - manual promotion from `staging`
- Feature branch previews for UI components

## 12. Documentation
- Use docstrings (for Python), YARD (for Ruby), and descriptive README files
- Maintain `docs/` directory for user and developer documentation
- `docs/architecture/` for architecture decision records (ADRs)
- `docs/runbooks/` for operational procedures
- System diagram in `docs/architecture/system_diagram.md`
- LLM-optimized documentation with clear sections and machine-readable formatting

## 13. Error Handling & Logging
- Standardized error handling patterns for each language
- Structured logging with common fields:
  - Request ID
  - Timestamp
  - Log level
  - Service name
  - User context (when applicable)
- Log levels used consistently:
  - ERROR: Exception conditions
  - WARN: Unexpected situations that can be recovered from
  - INFO: Key application events
  - DEBUG: Detailed information for troubleshooting
- Log aggregation with Grafana Loki or similar

## 14. Compliance & Secrets Management
- Follow SOC2 & GDPR practices where relevant
- Secrets are never stored in source code
- Kubernetes Secrets managed and rotated through Porter
- Data classification guidelines in `docs/compliance/data_classification.md`
- Annual security review processes

## 15. Monitoring & Observability
- Use Prometheus and Grafana dashboards
- Ensure metrics are exposed from all services
- Standard metrics to track:
  - Request rate, error rate, and duration
  - Resource utilization (CPU, memory)
  - Business-specific metrics
- Alerting rules defined in `.github/alerting/`
- On-call rotation schedule

## 16. Dependency Management
- Dependencies updated regularly and reviewed via Dependabot or Renovate
- Vulnerability scanning in CI pipeline
- Lock files committed to repository
- Dependency review part of PR process

## 17. LLM-Assisted Code Generation
- Code template files in `ai-assist/templates/` for consistent generation
- Auto-documented code blocks with standardized header comments
- Consistent function signatures with complete type annotations
- Modular code structure optimized for AI comprehension and generation
- "Chain of thought" comments for complex algorithms to assist future LLM understanding


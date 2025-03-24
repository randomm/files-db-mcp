# CLAUDE.md - LLM Assistant Guidelines

## Development Commands
- Build: TBD (Use language-specific commands once implemented)
- Lint: Follow language conventions in `ai-assist/guidelines/code_generation.md`
- Test: Test using appropriate framework (Jest, pytest, etc.)
- Single test: Use framework-specific command for running individual tests

## Code Style Guidelines
- Follow language-specific conventions in `ai-assist/guidelines/code_generation.md`
- Python: PEP 8, Google docstrings, type hints, snake_case functions, PascalCase classes
- JavaScript: Airbnb style, camelCase functions, PascalCase classes/components
- Git: Lowercase commit prefixes (feat:, fix:, docs:, etc.)
- Error handling: Be explicit, return early, validate inputs, provide meaningful messages
- Security: Follow guidelines in `ai-assist/guidelines/security_review.md`
- Documentation: Explain why (not what), document all public functions/classes

## Project Structure
- Source code in `/src`
- Tests in `/tests`
- Documentation in `/docs`
- AI assistance files in `/ai-assist`

When analyzing code, prioritize readability over cleverness and maintain consistent naming conventions. Use proper error handling and follow security best practices from the security review guidelines.
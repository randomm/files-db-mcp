# Code Generation Guidelines

This document provides guidelines for AI assistants to generate and review code that aligns with project standards and best practices.

## Code Style and Conventions

### General Principles

- Follow the principle of least surprise
- Prioritize readability over cleverness
- Maintain consistent naming and formatting
- Aim for self-documenting code with clear naming

### Language-Specific Conventions

#### Python

- Follow PEP 8 style guidelines
- Use Google-style docstrings
- Use type hints for function parameters and return values
- Use snake_case for variables and functions
- Use PascalCase for classes
- Use UPPER_CASE for constants

#### JavaScript/TypeScript

- Follow Airbnb JavaScript Style Guide
- Use camelCase for variables and functions
- Use PascalCase for classes and React components
- Use types in TypeScript wherever possible
- Prefer arrow functions for callbacks
- Use async/await over Promises where appropriate

#### Other Languages

[Add guidelines for other languages used in the project]

## Common Patterns and Idioms

### Error Handling

- Be explicit about error cases
- Use try/except (or equivalent) sparingly and purposefully
- Return early to avoid deep nesting
- Validate inputs at function boundaries
- Provide meaningful error messages

### Asynchronous Programming

- Use async/await patterns consistently
- Handle errors in asynchronous code explicitly
- Avoid mixing different async patterns
- Consider timeouts for all external calls

### Testing Patterns

- Write tests first when possible (TDD approach)
- Structure tests using Arrange-Act-Assert pattern
- Mock external dependencies appropriately
- Test edge cases and error conditions

## Security Best Practices

- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Implement proper authentication and authorization checks
- Sanitize outputs to prevent XSS attacks
- Use secure defaults for all configurations
- Don't hardcode secrets or credentials
- Use prepared statements for database queries
- Implement proper rate limiting

## Performance Considerations

- Be mindful of algorithmic complexity
- Minimize database calls and optimize queries
- Use appropriate data structures for the task
- Consider caching for expensive operations
- Avoid premature optimization
- Profile code before optimizing

## Documentation Standards

### Code Comments

- Explain why, not what (the code should explain what)
- Comment complex algorithms or business logic
- Use TODO comments for future improvements
- Include references to issue numbers where relevant

### Function and Class Documentation

- Document all public functions and classes
- Clearly describe parameters and return values
- Document exceptions that might be thrown
- Include usage examples for complex functions

## Review Checklist

When reviewing code, check for the following:

- Code follows project style and conventions
- No obvious bugs or edge cases
- Proper error handling
- Appropriate test coverage
- Security considerations addressed
- Performance considerations addressed
- Clear and adequate documentation
- No unnecessary dependencies
- No duplicated code

## Implementation Guidelines

### Start with Structure

1. Begin by outlining the main components and their relationships
2. Define clear interfaces between components
3. Establish error handling strategies upfront

### Iterative Development

1. Implement a minimal working version first
2. Add tests for the basic functionality
3. Refine and expand with additional features
4. Continuously refactor to maintain code quality

### Code Generation Format

When generating code, use the following format:

```
[language filename]
[code content]
```

For example:

```python
# users.py

from typing import Optional, List
from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True
```
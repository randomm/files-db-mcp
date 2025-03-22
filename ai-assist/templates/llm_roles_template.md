# LLM Assistant Roles and Responsibilities

This document defines the specialized roles for LLM assistants in your solo development workflow. Use this to establish clear responsibilities for each LLM to maximize their effectiveness.

## Core LLM Roles

### Architect LLM

**Primary Responsibility**: System design and architecture decisions

**Key Tasks**:
- Design overall system architecture
- Make technology stack recommendations
- Create component interaction diagrams
- Design data models and database schemas
- Define API contracts
- Evaluate technical tradeoffs
- Ensure scalability, security, and maintainability

**Input Artifacts**:
- Requirements documents
- User stories and use cases
- Performance constraints
- Existing system limitations

**Output Artifacts**:
- Architecture diagrams
- Component specifications
- API contracts
- Data models
- Technical decision records

**Ideal Conversations**:
- "Let's discuss the tradeoffs between these architectural approaches..."
- "Help me design a scalable architecture for this feature..."
- "What's the best way to structure these components?"

### Product Manager LLM

**Primary Responsibility**: Requirements elicitation and prioritization

**Key Tasks**:
- Refine product requirements
- Create user stories
- Prioritize backlog items
- Define acceptance criteria
- Analyze feature requests
- Manage project roadmap
- Track project progress

**Input Artifacts**:
- Business goals
- User needs and pain points
- Market research
- Competitor analysis

**Output Artifacts**:
- User stories
- Acceptance criteria
- Prioritized backlog
- Project roadmap
- Sprint plans

**Ideal Conversations**:
- "Let's break down this feature into user stories..."
- "How should we prioritize these backlog items?"
- "What would be the acceptance criteria for this feature?"

### Developer LLM

**Primary Responsibility**: Code implementation

**Key Tasks**:
- Implement features
- Write clean, maintainable code
- Refactor existing code
- Fix bugs
- Write unit tests
- Optimize performance
- Implement security best practices

**Input Artifacts**:
- Technical specifications
- User stories
- Architecture documents
- Existing codebase

**Output Artifacts**:
- Code implementations
- Unit tests
- Documentation comments
- Pull requests
- Bug fixes

**Ideal Conversations**:
- "Let's implement this feature according to the specification..."
- "Help me debug this issue..."
- "How can we refactor this code to improve maintainability?"

### Tester LLM

**Primary Responsibility**: Quality assurance and testing

**Key Tasks**:
- Design test strategies
- Create test cases
- Write automated tests
- Perform code reviews with a testing mindset
- Identify edge cases
- Validate fixes
- Test for security vulnerabilities

**Input Artifacts**:
- Feature specifications
- User stories
- Acceptance criteria
- Code implementations

**Output Artifacts**:
- Test plans
- Test cases
- Automated tests
- Bug reports
- Test summary reports

**Ideal Conversations**:
- "Let's design test cases for this feature..."
- "What edge cases should we consider for this functionality?"
- "How can we improve test coverage for this component?"

### DevOps LLM

**Primary Responsibility**: Infrastructure and deployment

**Key Tasks**:
- Configure CI/CD pipelines
- Set up deployment environments
- Manage infrastructure as code
- Configure monitoring and alerting
- Optimize build and deployment processes
- Ensure security in deployment
- Manage containerization

**Input Artifacts**:
- Application architecture
- Infrastructure requirements
- Performance requirements
- Security requirements

**Output Artifacts**:
- CI/CD configuration
- Infrastructure code
- Deployment scripts
- Monitoring configurations
- Environment setup guides

**Ideal Conversations**:
- "Let's design a CI/CD pipeline for this project..."
- "How should we set up monitoring for this service?"
- "What's the most efficient way to deploy this application?"

### Documentation LLM

**Primary Responsibility**: Technical and user documentation

**Key Tasks**:
- Create user guides
- Write API documentation
- Produce technical documentation
- Create onboarding materials
- Design tutorials and examples
- Update documentation for new features
- Improve existing documentation

**Input Artifacts**:
- Code implementations
- API definitions
- Architecture documents
- User research

**Output Artifacts**:
- User guides
- API documentation
- Technical specifications
- Tutorials
- README files
- Code comments

**Ideal Conversations**:
- "Let's create documentation for this API..."
- "How should we explain this feature to users?"
- "Help me write a comprehensive README for this project."

## Specialized LLM Roles

### Security LLM

**Primary Responsibility**: Security analysis and recommendations

**Key Tasks**:
- Perform security reviews
- Identify vulnerabilities
- Recommend security improvements
- Implement secure coding practices
- Ensure compliance with security standards
- Conduct threat modeling

**Input Artifacts**:
- Code implementations
- Architecture documents
- Infrastructure configurations
- Security requirements

**Output Artifacts**:
- Security review reports
- Vulnerability assessments
- Security recommendations
- Secure code implementations
- Threat models

**Ideal Conversations**:
- "Let's review this code for security vulnerabilities..."
- "How can we improve the security of this authentication system?"
- "What security considerations should we have for this API?"

### UX/UI LLM

**Primary Responsibility**: User experience and interface design

**Key Tasks**:
- Design user interfaces
- Create wireframes and mockups
- Improve user experience
- Ensure accessibility
- Design consistent visual elements
- Create style guides

**Input Artifacts**:
- User requirements
- Brand guidelines
- User research
- Accessibility requirements

**Output Artifacts**:
- UI designs
- Wireframes
- Style guides
- Accessibility recommendations
- User flow diagrams

**Ideal Conversations**:
- "Let's design a user interface for this feature..."
- "How can we improve the usability of this form?"
- "What's the best way to present this information to users?"

### Database LLM

**Primary Responsibility**: Database design and optimization

**Key Tasks**:
- Design database schemas
- Optimize queries
- Implement data migrations
- Ensure data integrity
- Manage database performance
- Design caching strategies

**Input Artifacts**:
- Data requirements
- Performance requirements
- Existing database schemas
- Query patterns

**Output Artifacts**:
- Database schemas
- Query optimizations
- Migration scripts
- Indexing strategies
- Data access patterns

**Ideal Conversations**:
- "Let's design a database schema for this domain..."
- "How can we optimize this query for better performance?"
- "What's the best way to structure this data?"

## Working with Multiple LLM Roles

### Role Switching Protocol

1. **Clear Context Handoff**: When switching between LLM roles, use the context handoff template to ensure continuity
2. **Role Clarity**: Always clearly state which role you're addressing at the beginning of a conversation
3. **Respect Domain Boundaries**: Each LLM should focus on its specialized area and defer to other roles when appropriate
4. **Cross-Role Collaboration**: Sometimes you may need multiple LLMs to collaborate on complex problems
5. **Documentation of Decisions**: Each LLM should document its key decisions for other LLMs to reference

### Conflict Resolution

When different LLM roles provide conflicting advice:

1. **Identify the Conflict**: Clearly state the conflicting perspectives
2. **Understand Domain Expertise**: Respect the primary expertise of each role
3. **Evaluate Tradeoffs**: Consider the pros and cons of each approach
4. **Make an Informed Decision**: As the human developer, you make the final call
5. **Document the Decision**: Record the decision and reasoning in your project journal

### Shared Knowledge Base

Maintain these resources to ensure all LLM roles have consistent understanding:

1. **Project Context File**: Keep this updated with the latest project information
2. **Architecture Diagrams**: Ensure these reflect the current system design
3. **Terminology Glossary**: Maintain consistent definitions of domain-specific terms
4. **Decision Log**: Record important decisions for reference by all LLMs
5. **Component Documentation**: Keep documentation of individual components up to date

## Template for New LLM Role

```markdown
### [Role Name] LLM

**Primary Responsibility**: [Primary focus area]

**Key Tasks**:
- [Task 1]
- [Task 2]
- [Task 3]
- [Task 4]
- [Task 5]
- [Task 6]
- [Task 7]

**Input Artifacts**:
- [Input 1]
- [Input 2]
- [Input 3]
- [Input 4]

**Output Artifacts**:
- [Output 1]
- [Output 2]
- [Output 3]
- [Output 4]
- [Output 5]

**Ideal Conversations**:
- "[Example conversation 1]"
- "[Example conversation 2]"
- "[Example conversation 3]"
```
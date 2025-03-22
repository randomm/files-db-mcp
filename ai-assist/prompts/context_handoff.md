# LLM Context Handoff Template

This template helps you efficiently transfer context between different LLM assistants. Use this to ensure continuity and consistency when switching between specialized LLM roles.

## Basic Handoff Template

```
# Context Handoff: [Current Task/Component]

## Session Summary
I've been working with [Previous LLM Role] on [task/component]. I'm now switching to you as [New LLM Role] to [purpose of switch].

## Project Context
- Project: [Project Name]
- Current Component: [Component Name]
- Current Task: [Task Description]
- Related Files: [List of relevant files]

## Progress Summary
- [Key point 1]
- [Key point 2]
- [Key point 3]

## Decisions Made
- [Decision 1]: [Reasoning]
- [Decision 2]: [Reasoning]

## Current Status
[Detailed description of the current state]

## Next Steps
I need you to:
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Questions/Challenges
- [Question/Challenge 1]
- [Question/Challenge 2]

## Reference Materials
[Any additional information, code snippets, etc.]
```

## Developer → Tester Handoff

```
# Context Handoff: Developer → Tester

## Session Summary
I've been working with a Developer LLM implementing [feature]. I'm now switching to you as a Tester LLM to verify this implementation works as expected.

## Project Context
- Project: [Project Name]
- Feature: [Feature Name]
- Files Changed: [List of modified files]
- Dependencies: [List of dependencies]

## Implementation Details
- [Key implementation detail 1]
- [Key implementation detail 2]
- [Key algorithm/approach used]
- [Edge cases handled]

## Expected Behavior
- [Expected behavior 1]
- [Expected behavior 2]
- [Performance expectations]

## Testing Needed
I need you to:
1. Design test cases covering the functionality
2. Include edge cases and error scenarios
3. Create test scripts to verify the implementation
4. Consider integration with existing systems

## Known Limitations
- [Limitation 1]
- [Limitation 2]

## Code Reference
```[language]
[Relevant code snippet]
```
```

## Architect → Developer Handoff

```
# Context Handoff: Architect → Developer

## Session Summary
I've been working with an Architect LLM designing [component]. I'm now switching to you as a Developer LLM to implement this design.

## Architecture Context
- Project: [Project Name]
- Component: [Component Name]
- Purpose: [Brief description of purpose]
- Architecture Diagram: [ASCII/text diagram]

## Design Decisions
- [Decision 1]: [Reasoning]
- [Decision 2]: [Reasoning]
- [Decision 3]: [Reasoning]

## Technical Specifications
- Programming Language: [Language]
- Frameworks/Libraries: [List]
- APIs/Interfaces: [List]
- Data Models: [Description]

## Implementation Requirements
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

## Performance/Security Considerations
- [Consideration 1]
- [Consideration 2]

## Implementation Steps
I need you to:
1. Create the basic structure
2. Implement core functionality
3. Add error handling and edge cases
4. Document the implementation

## Reference Materials
[Any additional diagrams, specs, examples]
```

## Product Manager → Architect Handoff

```
# Context Handoff: Product Manager → Architect

## Session Summary
I've been working with a Product Manager LLM defining requirements for [feature]. I'm now switching to you as an Architect LLM to design a solution.

## Feature Requirements
- Primary Goal: [Main goal]
- User Stories:
  1. [User story 1]
  2. [User story 2]
- Technical Constraints:
  1. [Constraint 1]
  2. [Constraint 2]

## User Experience Expectations
- [UX requirement 1]
- [UX requirement 2]

## Business Context
- Priority: [High/Medium/Low]
- Timeline: [Expected timeline]
- Stakeholders: [List of stakeholders]
- Success Metrics: [How success will be measured]

## Current System Context
- Related Components: [List of components]
- Integration Points: [Systems to integrate with]
- Existing Patterns: [Patterns to follow]

## Design Needs
I need you to:
1. Create a high-level architectural design
2. Identify components and their interactions
3. Suggest appropriate technologies and frameworks
4. Highlight potential technical challenges
5. Provide a rough implementation plan

## Questions/Concerns
- [Question 1]
- [Question 2]

## Reference Materials
[Any mockups, diagrams, or similar existing features]
```

## Solo Developer Tips for Context Handoffs

1. **Maintain a central knowledge document** that all LLMs can reference to ensure consistency
2. **Be explicit about the role transition** - tell the new LLM exactly what role it's taking
3. **Summarize key decisions** to avoid contradictory approaches between LLMs
4. **Include relevant code snippets** directly in the handoff prompt
5. **Create project glossaries** for domain-specific terminology
6. **Reference previous sessions** if you're returning to a role after switching
7. **Ask for a summary from each LLM** before switching to capture their understanding
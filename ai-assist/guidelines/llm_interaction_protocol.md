# LLM Interaction Protocol

This document provides guidelines for effective interaction with AI language models during software development.

## Prompt Crafting Best Practices

### Structuring Effective Prompts

1. **Be specific and detailed**: Provide clear context and desired outcome
2. **Use structured formats**: Organize complex prompts with clear sections
3. **Include examples**: Demonstrate the expected format and style
4. **State constraints**: Define limitations and requirements
5. **Request reasoning**: Ask the LLM to explain its approach

### Prompt Templates

#### Code Generation Prompt

```
I need to implement [feature description].

Context:
- Project uses [language/framework]
- Following [specific pattern/style]
- Need to handle [specific requirements/edge cases]

Existing code that this needs to integrate with:
```[existing code]```

Please generate:
1. Implementation code
2. Unit tests
3. Brief explanation of your approach
```

#### Code Review Prompt

```
Please review the following code for:
1. Bugs or logical errors
2. Performance issues
3. Security vulnerabilities
4. Adherence to best practices
5. Readability and maintainability

Code to review:
```[code to review]```

Project context:
- [Language/framework]
- [Coding standards]
- [Performance requirements]
```

#### Problem-Solving Prompt

```
I'm facing the following issue: [detailed description].

Relevant context:
- [Environment details]
- [Observed behavior]
- [Expected behavior]
- [Steps already tried]

Error output:
```[error logs/outputs]```

Please help me:
1. Diagnose the most likely causes
2. Suggest solutions in order of probability
3. Explain the reasoning behind your suggestions
```

## Context Provision Guidelines

### Essential Context Elements

1. **Project information**: Language, framework, dependencies
2. **Architectural context**: System design, component interactions
3. **Existing code**: Relevant files and functions
4. **Requirements**: Functional and non-functional requirements
5. **Constraints**: Performance, security, compatibility requirements

### Effective Context Sharing

1. **Start broad, then narrow**: Begin with high-level context, then provide specifics
2. **Prioritize relevance**: Focus on information directly related to the task
3. **Include examples**: Provide examples of similar solutions within the codebase
4. **Update context**: Clarify misconceptions and add missing information
5. **Summarize context**: Ask the LLM to summarize its understanding to verify comprehension

## Review and Verification Process

### Code Review Checklist

1. **Correctness**: Does the solution solve the stated problem?
2. **Completeness**: Are all requirements addressed?
3. **Consistency**: Does it follow the project's patterns and conventions?
4. **Security**: Are there potential security issues?
5. **Performance**: Are there performance concerns?
6. **Readability**: Is the code clear and maintainable?
7. **Error handling**: Are errors properly caught and handled?
8. **Edge cases**: Are edge cases considered?

### Verification Steps

1. **Manual review**: First, review the code yourself
2. **Test execution**: Run tests to verify functionality
3. **Code integration**: Ensure it works with the existing codebase
4. **Refinement requests**: Ask for specific improvements
5. **Final verification**: Confirm all requirements are met

## Confidence and Uncertainty Communication

### Confidence Indicators

When interacting with an LLM, look for these indicators of confidence:

1. **Consistency**: Responses remain consistent across rephrased questions
2. **Specificity**: Detailed and precise answers versus vague responses
3. **Reasoning**: Clear explanation of thought process
4. **Alternative solutions**: Offering multiple approaches with trade-offs
5. **Limitations acknowledgment**: Recognition of constraints or knowledge boundaries

### Handling Uncertainty

When the LLM expresses uncertainty:

1. **Break down the problem**: Divide complex issues into smaller parts
2. **Provide more context**: Fill in knowledge gaps
3. **Ask clarifying questions**: Address specific uncertainties
4. **Verify externally**: Fact-check critical information
5. **Explore alternatives**: Consider multiple approaches

## Human-LLM Collaboration

### Effective Collaboration Patterns

1. **Iterative refinement**: Start with a baseline and improve incrementally
2. **Divide and conquer**: Assign appropriate subtasks to LLM versus human
3. **Expertise complementation**: Use LLM for knowledge-intensive tasks, humans for judgment
4. **Parallel exploration**: Explore multiple solutions simultaneously
5. **Review and revise**: Human review of LLM outputs with feedback loop

### Collaboration Anti-patterns

1. **Blind acceptance**: Implementing LLM suggestions without review
2. **Vague requests**: Providing insufficient context or requirements
3. **Mismatched expectations**: Expecting the LLM to understand unstated requirements
4. **Context overload**: Providing excessive irrelevant information
5. **Tool misuse**: Using LLM for tasks better suited to other tools

## Handoff Processes

### Documenting LLM Interactions

1. **Record key prompts**: Save effective prompts for reuse
2. **Capture reasoning**: Document why specific approaches were chosen
3. **Note limitations**: Record any issues or constraints identified
4. **Version outputs**: Track changes through iterations
5. **Link to requirements**: Connect LLM outputs to project requirements

### Transition to Human Workflows

1. **Code review process**: Submit LLM-generated code through standard review
2. **Documentation updates**: Ensure documentation reflects LLM-assisted work
3. **Knowledge sharing**: Communicate insights from LLM interactions
4. **Issue tracking**: Create or update issues based on LLM findings
5. **Continuous improvement**: Refine LLM interaction process based on outcomes

## Ethics and Best Practices

### Ethical Guidelines

1. **Transparency**: Be clear about LLM usage in development
2. **Attribution**: Properly attribute work done with LLM assistance
3. **Human oversight**: Maintain human responsibility for decisions
4. **Data privacy**: Avoid sharing sensitive or proprietary information
5. **Bias awareness**: Watch for and correct potential biases in LLM outputs

### Responsible Usage

1. **Appropriate tasks**: Use LLMs for suitable tasks, not as a replacement for critical thinking
2. **Security considerations**: Validate security-sensitive code
3. **Balance efficiency and quality**: Don't sacrifice quality for speed
4. **Continuous learning**: Use LLM interactions as learning opportunities
5. **Team inclusion**: Ensure all team members can benefit from LLM assistance
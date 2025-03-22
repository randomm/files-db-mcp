# LLM Roadmap and Backlog Management System

This document provides guidelines for an LLM to continuously manage and maintain a project's roadmap, backlog, and tickets through structured human interaction. It aligns with the project structure defined in `project_boilerplate.md` and ensures consistent, high-quality requirements management.

## Integration with Project Structure

This system works within the established project structure:
- `.tasks/README.md` - Overview of project structure
- `.tasks/backlog.md` - Prioritized product backlog items
- `.tasks/sprints/` - Sprint planning and retrospectives
- `.tasks/templates/` - Issue and task templates
- `.tasks/ROADMAP.md` - High-level product roadmap

## Continuous Management Approach

### 1. Initial Roadmap and Backlog Creation

Begin with a structured interview session to establish the foundation:

```
INTERVIEW PROMPT: I'd like to establish our project roadmap and initial backlog. 
Let's discuss the project vision, key features, timeline, and priorities.
```

Follow these steps:
1. Gather strategic vision and goals
2. Identify key user personas and needs
3. Define success metrics
4. Establish high-level timeline and phases
5. Identify initial feature set
6. Assess risks and constraints
7. Create initial roadmap document
8. Generate prioritized backlog items

### 2. Regular Check-in Sessions

Schedule recurring sessions to update and refine the roadmap and backlog:

```
CHECK-IN PROMPT: Let's review our roadmap and backlog progress. 
What updates or changes should we make based on recent developments?
```

During each session:
1. Review progress on current priorities
2. Discuss any changing requirements or priorities
3. Identify new insights or market changes
4. Update timelines as needed
5. Refine existing backlog items
6. Add new backlog items as needed
7. Update roadmap document with changes
8. Re-prioritize backlog based on current context

### 3. Ticket Management

Assist with creation and management of individual tickets:

```
TICKET PROMPT: Let's create a new ticket for [feature/bug/task]. 
Let's define the requirements, acceptance criteria, and technical details.
```

For each ticket:
1. Generate structured ticket using task metadata format:
   ```md
   --- 
   id: TASK-[ID]
   type: feature|bug|refactor
   priority: high|medium|low
   status: todo
   assignee: [user]
   due: YYYY-MM-DD
   ---
   
   # [Task Title]
   
   ## Description
   [Clear description]
   
   ## Acceptance Criteria
   - [ ] Criteria 1
   - [ ] Criteria 2
   
   ## Technical Notes
   [Technical considerations]
   ```
2. Ensure alignment with roadmap priorities
3. Link related tickets when necessary
4. Maintain consistent labeling and structure

### 4. Sprint Planning Assistance

Support sprint planning sessions:

```
SPRINT PROMPT: Let's plan our next sprint. What should we prioritize 
from the backlog based on our current roadmap and team capacity?
```

During sprint planning:
1. Review roadmap to confirm priorities
2. Assess team capacity and velocity
3. Recommend backlog items for the sprint
4. Help estimate complexity/effort
5. Create sprint planning document in `.tasks/sprints/`
6. Update ticket status for selected items
7. Define sprint goals and success metrics

### 5. Progress Tracking and Adaptation

Maintain ongoing awareness of project status:

```
PROGRESS PROMPT: Let's review our current progress. What's on track, 
what's at risk, and what adjustments should we make?
```

For progress tracking:
1. Analyze completed vs. planned work
2. Identify bottlenecks or blockers
3. Suggest roadmap or backlog adjustments
4. Update status of tickets
5. Document lessons learned
6. Recommend process improvements

## LLM Interview Techniques

### Key Question Categories

1. **Status Questions**
   - "What progress has been made since our last review?"
   - "Which items are at risk of missing their deadlines?"
   - "What unexpected challenges have emerged?"

2. **Priority Questions**
   - "Has anything changed that would affect our priorities?"
   - "Do we need to reprioritize based on recent feedback or market changes?"
   - "What's the most important goal for the next [week/month/quarter]?"

3. **Refinement Questions**
   - "Should we break down any backlog items into smaller tasks?"
   - "Do any requirements need clarification or additional detail?"
   - "Are our acceptance criteria specific and measurable enough?"

4. **Strategic Questions**
   - "Are we still aligned with our overall product vision?"
   - "Have market conditions or user needs changed since our last review?"
   - "Should we adjust our roadmap timeline based on current progress?"

5. **Process Questions**
   - "How is the team's velocity? Do we need to adjust our sprint capacity?"
   - "Are there process improvements we should implement?"
   - "What tools or resources would help the team be more effective?"

### Continuous Improvement Cycle

Follow this cycle for ongoing management:
1. **Review** current state of roadmap and backlog
2. **Identify** gaps, changes, or issues
3. **Update** documents with new information
4. **Prioritize** based on current context
5. **Communicate** changes to stakeholders
6. **Repeat** at regular intervals

## Document Maintenance Guidelines

### Roadmap Updates

When updating `.tasks/ROADMAP.md`:
1. Maintain version history section at the top
2. Use consistent phase naming and structure
3. Track changes to key milestones
4. Ensure alignment with business objectives
5. Balance detail with flexibility
6. Include visual timeline when possible

### Backlog Management

When updating `.tasks/backlog.md`:
1. Maintain strict prioritization (high/medium/low)
2. Include rationale for priority changes
3. Ensure each item has clear acceptance criteria
4. Cross-reference related items
5. Tag items with appropriate categories
6. Remove or archive completed items

### Ticket Creation

When creating new tickets:
1. Follow the prescribed metadata format
2. Ensure unique ID assignment
3. Link to parent feature when applicable
4. Include specific, testable acceptance criteria
5. Add relevant technical details
6. Assign appropriate priority level

## Actionable Templates

### Roadmap Template

```md
# Project Roadmap: [Project Name]
Last Updated: [Date]

## Version History
- v1.0 ([Date]) - Initial roadmap
- v1.1 ([Date]) - [Brief description of changes]

## Strategic Vision
[Vision statement]

## Success Metrics
- [Metric 1]: [Target]
- [Metric 2]: [Target]

## Timeline Overview
[Q1 2023] - [Phase 1 Name]
[Q2 2023] - [Phase 2 Name]
[Q3-Q4 2023] - [Phase 3 Name]

## Phase 1: [Phase Name] - [Timeframe]
[Description]

### Key Deliverables:
- [Deliverable 1] - [Target date]
- [Deliverable 2] - [Target date]

## Phase 2: [Phase Name] - [Timeframe]
...

## Risk Assessment
- [Risk 1]: [Mitigation strategy]
- [Risk 2]: [Mitigation strategy]
```

### Sprint Planning Template

```md
# Sprint [Number] Planning
Sprint Dates: [Start Date] - [End Date]

## Sprint Goals
- [Goal 1]
- [Goal 2]

## Team Capacity
- Available story points: [Number]
- Team members: [Number]

## Selected Backlog Items
- [ ] TASK-[ID]: [Title] ([Priority], [Story Points])
- [ ] TASK-[ID]: [Title] ([Priority], [Story Points])

## Sprint Risk Assessment
- [Risk 1]: [Mitigation plan]
- [Risk 2]: [Mitigation plan]

## Definition of Done
- [Criterion 1]
- [Criterion 2]
```

### Sprint Retrospective Template

```md
# Sprint [Number] Retrospective
Sprint Dates: [Start Date] - [End Date]

## Sprint Goals Review
- [Goal 1]: [Achieved/Partially Achieved/Not Achieved]
- [Goal 2]: [Achieved/Partially Achieved/Not Achieved]

## Metrics
- Story points completed: [Number]/[Total Planned]
- Tickets completed: [Number]/[Total Planned]
- Bugs identified: [Number]

## What Went Well
- [Item 1]
- [Item 2]

## What Could Be Improved
- [Item 1]
- [Item 2]

## Action Items
- [ ] [Action 1] - Assigned to [Person], Due [Date]
- [ ] [Action 2] - Assigned to [Person], Due [Date]
```

## Implementation Guidelines

1. Create these files at project initiation
2. Schedule regular review sessions with stakeholders
3. Maintain consistency across all documents
4. Keep historical versions for reference
5. Ensure all team members have access to up-to-date documents
6. Link roadmap items to specific backlog entries
7. Update documents immediately after decision-making sessions

By following this system, an LLM can effectively manage and maintain a project's roadmap and backlog through ongoing collaboration with stakeholders, ensuring alignment with business goals and maintaining clear, actionable development priorities.
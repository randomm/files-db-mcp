# Task Management for Files-DB-MCP

This directory contains the project management files for the Files-DB-MCP project, a local vector database for software files that provides a fast MCP interface for LLM coding agents.

## Directory Structure

- `README.md` - This file, providing an overview of the task management system
- `ROADMAP.md` - High-level project roadmap with phases and key deliverables
- `backlog.md` - Prioritized list of product backlog items
- `sprints/` - Sprint planning and retrospective documentation
- `templates/` - Issue and task templates

## Task Structure

Tasks in this project follow a standardized format:

```md
--- 
id: TASK-XXX
type: feature|bug|refactor
priority: high|medium|low
status: todo|in-progress|review|done
assignee: [username]
due: YYYY-MM-DD
---

# Task Title

## Description
Clear description of the task.

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
```

## Task Types

- `feature`: New functionality or enhancement
- `bug`: Fix for an issue or unexpected behavior
- `refactor`: Code improvement without changing functionality
- `docs`: Documentation-related tasks
- `infra`: Infrastructure and build-related tasks

## Priority Levels

- `high`: Critical for project success, must be completed first
- `medium`: Important but not blocking other work
- `low`: Nice to have, can be completed if time permits

## Status Values

- `todo`: Not yet started
- `in-progress`: Currently being worked on
- `review`: Ready for review/testing
- `done`: Completed and verified

## Task Management Process

1. Tasks are initially added to the `backlog.md` file
2. During sprint planning, selected tasks are moved to the current sprint file
3. Task status is updated as work progresses
4. Completed sprints are archived in the `sprints/` directory
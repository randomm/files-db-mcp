---
id: TASK-016
type: bugfix
priority: high
status: todo
---

# Fix Docker Compose environment health check issues

## Description
The Docker Compose setup is currently failing to start properly due to health check issues with the vector-db container. This prevents the entire system from functioning as intended. The issue needs to be fixed to enable the one-command Docker Compose environment as specified in TASK-001.

## Acceptance Criteria
- [ ] Identify the root cause of the vector-db container health check failure
- [ ] Update Docker Compose configuration or health check parameters to resolve the issue
- [ ] Ensure all containers start successfully and pass health checks
- [ ] Verify the system can be started with a single command
- [ ] Test that the MCP interface is accessible at the specified port
- [ ] Confirm that file indexing works correctly in the containerized environment
- [ ] Update documentation if necessary

## Related Tasks
- TASK-001: Set up one-command Docker Compose environment (depends on)

## Notes
- The health check for vector-db is failing, preventing the dependent files-db-mcp service from starting
- Current health check configuration may need adjustment or the Qdrant service might need additional time to initialize
- The solution should ensure reliability and consistency across different environments
---
id: TASK-022
type: infra
priority: critical
status: todo
---

# Fix CI Pipeline Issues After Repository Reorganization

## Description
The CI pipeline is not functioning correctly after the repository reorganization in TASK-019 and TASK-020. The workflows need to be updated to reflect the new file structure, and several tests are failing in the CI environment. This task involves fixing these issues to ensure the CI pipeline can effectively validate code changes.

## Acceptance Criteria
- [ ] Update GitHub Actions workflow files to reference correct paths after reorganization
- [ ] Fix Docker build process in CI to work with new directory structure
- [ ] Ensure test discovery finds all tests in the new directory structure
- [ ] Confirm test coverage reporting works correctly
- [ ] Fix any environment-specific test failures in CI
- [ ] Add status badges to README.md for CI/CD status
- [ ] Document CI pipeline setup and troubleshooting in developer documentation

## Technical Notes
- The `.github/workflows/ci.yml` file needs to be updated to reflect the new directory structure
- Docker build context may need adjustments due to the new `.docker` directory
- Test discovery patterns may need updating to find tests in the reorganized `/tests` directory
- Coverage configuration likely needs updating to reflect new source code paths
- CI environment may have different permissions than local development environment

## Dependencies
- TASK-019: Repository Structure Cleanup
- TASK-020: Continue Repository Cleanup for Elegant Structure
- TASK-015: CI/CD Pipeline Implementation

## Related Tasks
- TASK-012: Fix Test Suite Issues (some overlap in test fixes)
- TASK-018: Prepare v0.1.0 Beta Release (depends on working CI)
---
id: TASK-019
type: cleanup
priority: high
status: done
---

# Repository Structure Cleanup and Organization

## Description
The repository root directory contains numerous files that need to be properly organized, moved to appropriate locations, or removed if unnecessary. This creates maintenance challenges, makes the repository harder to navigate, and can cause confusion for new contributors. A comprehensive cleanup is needed to ensure a clean, organized repository structure that follows best practices.

## Acceptance Criteria
- [x] Audit all files in the repository root directory
- [x] Categorize each file as:
  - Essential to be in root
  - Needs to be moved to appropriate subdirectory
  - Temporary/generated (should be removed and added to .gitignore)
  - Obsolete/unused (should be deleted)
- [x] Move configuration files to a `config` directory where appropriate
- [x] Ensure all temporary files are properly added to .gitignore
- [x] Consolidate test-related files to the `tests` directory
- [x] Move scripts to the `scripts` directory
- [x] Update documentation to reflect the new structure
- [x] Ensure no functionality is broken by the reorganization
- [x] Create a clear README section on repository structure

## Files to Assess (Preliminary List)
- `.coverage` files (likely temporary, should be in .gitignore)
- `.cursor` directory (IDE-specific, evaluate if needed)
- `.docker` directory (evaluate purpose and location)
- `.files-db-mcp` directory (evaluate if this should be in .gitignore)
- `CLAUDE.md` (determine purpose, might need a better location)
- `claude_mcp_server.py` (assess if it should be in src)
- `claude_mcp_test_summary.md` (likely belongs in test documentation)
- `conversation_summary.md` (determine purpose and appropriate location)
- `coverage.xml` (add to .gitignore, is a generated file)
- `coverage_html` directory (add to .gitignore, is a generated directory)
- `server.log` (should be in .gitignore)
- `test_mcp.py` (should be in the tests directory)
- `test-coverage-message.txt` (determine purpose, might belong in tests)

## Implementation Details

1. **Root Directory Assessment**
   - Determine which files are essential in root:
     - `README.md`, `LICENSE`, `pyproject.toml` typically belong in root
     - Configuration files like `.gitignore`, `.dockerignore` should stay in root
     - `Dockerfile`, `docker-compose.yml` are conventionally kept in root
     - Installation scripts and runners (`install.sh`, `run.sh`, `setup.sh`) often are kept in root for convenience

   - Identify files to be moved:
     - Python code files should be in `src` or appropriate module directories
     - Test files should be in `tests`
     - Documentation should be in `docs`
     - Helper scripts should be in `scripts`

   - Identify files to be added to .gitignore:
     - Generated files (`.coverage`, `coverage.xml`, `*.log`, etc.)
     - IDE-specific directories (`.vscode`, `.idea`, etc.)
     - Local environment files that shouldn't be shared

2. **Directory Structure Recommendations**
   - Consider creating:
     - `config/` for configuration files that don't need to be in root
     - `tools/` for development and maintenance tools
     - `examples/` for example usage patterns
     - Ensure tests are properly organized by test type (unit, integration)

3. **Cleanup Process**
   - Create proper backups before moving/deleting files
   - Implement changes incrementally, with testing after each significant change
   - Update import paths in code after moving Python files
   - Ensure CI/CD pipeline still works after reorganization

## Testing Approach
After reorganization, verify:
- All tests still pass
- Application can be built and run
- Installation scripts still work
- Documentation is accurate and up-to-date
- CI/CD pipeline functions as expected

## Related Tasks
- TASK-015: Create CI/CD pipeline with Docker (might need updates after reorganization)
- TASK-011: Comprehensive documentation (will need updates to reflect new structure)
- TASK-018: Prepare v0.1.0 Beta Release (this cleanup should be completed before release)

## Notes
This task is critical for both maintainability and the upcoming beta release. A well-organized repository is essential for project longevity and contributor onboarding. The cleanup should focus on making the repository structure intuitive and aligned with Python project best practices.
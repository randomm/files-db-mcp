---
id: TASK-020
type: cleanup
priority: high
status: done
---

# Continue Repository Cleanup for Elegant, Minimal Structure

## Description
While TASK-019 made significant progress in organizing the repository, there's still work needed to make the codebase truly elegant and minimal. The repository contains too many files in the root directory and needs further consolidation to create a clean, professional structure that reflects the tool's purpose as a lightweight, elegant utility.

## Acceptance Criteria
- [x] Further reduce root directory files to absolute minimum (README.md, LICENSE, pyproject.toml, and essential Docker files)
- [x] Move all Docker-related files to a `.docker` directory, with only main Dockerfile in root
- [x] Consolidate installation scripts into a single `install` directory
- [x] Move all configuration files to the `config` directory
- [x] Restructure `.github` directory with proper CI workflows and templates
- [x] Add proper LICENSE file if missing
- [x] Clean up any leftover temporary/cache files (like `.coverage` files)
- [x] Update all documentation to reflect the new structure
- [x] Update imports and file references in code to match new structure
- [x] Ensure Docker builds still work after restructuring

## Files to Move to Appropriate Locations
- `.pre-commit-config.yaml` → `config/`
- `Dockerfile.test` → `.docker/`
- `Makefile` → Move commands to documented scripts in `scripts/`
- `CLAUDE.md` → `ai-assist/` or `docs/`
- `docker-compose.ci.yml` → `.docker/`
- `install.sh` & `setup.sh` → `install/`
- `run.sh` → `scripts/`
- `.coverage` files → Remove, add to .gitignore
- `.dockerignore` → Keep in root or move to `.docker/` with symlink

## Implementation Details

### Root Directory Cleanup
- Root directory should contain only:
  - `README.md` - Main documentation entry point
  - `LICENSE` - Open source license
  - `pyproject.toml` - Python package configuration
  - `Dockerfile` - Main build file
  - `.gitignore` - Git ignore patterns
  - `docker-compose.yml` - Main compose file
  - Any other absolutely essential files that must be in root

### Directory Structure Improvements
1. **Create Proper Installation Directory**
   - Move all installation scripts to `install/`
   - Update documentation to reference new script locations
   - Ensure backward compatibility with any existing installation instructions

2. **Enhance Docker Organization**
   - Create `.docker/` for Docker-related files
   - Move all test and CI Docker configurations there
   - Update CI pipelines to reference new locations

3. **Configuration Consolidation**
   - Move all configuration files to `config/`
   - Use symlinks if necessary for tools that require config in root

### Code Updates
- Update any hardcoded paths in the codebase
- Ensure all imports and file references reflect new structure
- Update scripts to handle the new directory layout

## Testing Approach
- Verify Docker builds work correctly after restructuring
- Test installation process with new script locations
- Run all existing tests to ensure functionality is preserved
- Test on a fresh system to verify installation still works

## Related Tasks
- TASK-019: Repository Structure Cleanup and Organization (predecessor)
- TASK-018: Prepare v0.1.0 Beta Release (dependent on clean structure)

## Notes
This task is focused on creating a minimal, elegant codebase structure that follows industry best practices while reducing clutter. The goal is to make the repository as clean and professional as possible before the beta release, reflecting the tool's purpose as a lightweight utility.
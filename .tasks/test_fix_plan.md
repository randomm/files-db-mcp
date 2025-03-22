# Test Suite Fix Plan (TASK-012)

## 1. File Processor Test Fixes

### Issues
- Tests attempt to create directories in invalid locations
- Permissions errors when manipulating test directories

### Solution
- Use `tmp_path` pytest fixture for temporary directory creation
- Mock filesystem operations instead of actually creating files
- Patch `os.makedirs` in tests to prevent actual file creation

## 2. SSE Interface Test Fixes

### Issues
- Coroutine 'SSEInterface._indexing_progress_task' never awaited
- Asyncio test setup incomplete
- Missing event loop for async tests

### Solution
- Add proper pytest-asyncio fixture setup
- Patch asyncio.create_task in __init__ method
- Use AsyncMock for proper coroutine mocking
- Set up event loop for each test with proper scope

## 3. Linting Fixes

### Issues
- 74 linting errors reported by ruff
- Unused imports
- String conversion issues
- Magic values in tests

### Solution
- Run `ruff --fix` to auto-fix 49 issues
- Manually fix remaining issues:
  - Remove unused imports
  - Use f-strings properly
  - Replace magic values with constants

## Implementation Plan

1. First pass: Fix linting issues
   - Apply automatic fixes
   - Clean up imports
   - Fix string formatting

2. Second pass: Fix file_processor tests
   - Refactor to use temporary directories
   - Mock filesystem operations

3. Third pass: Fix SSE interface tests
   - Set up proper asyncio fixtures
   - Fix event loop issues

4. Final verification
   - Run complete test suite
   - Verify code coverage
   - Ensure CI pipeline passes
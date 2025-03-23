# Incremental Indexing in Files-DB-MCP

This document explains the incremental indexing feature in Files-DB-MCP, which optimizes performance by only processing files that have changed since the last indexing operation.

## Overview

Incremental indexing significantly improves performance when working with large codebases by:

1. Maintaining a state file with metadata about indexed files
2. Detecting which files have been added, modified, or deleted
3. Only processing the files that have changed
4. Tracking file metadata including content hashes, modification times, and file sizes

## How It Works

### File Tracking

Files-DB-MCP tracks the following metadata for each indexed file:

- **Content Hash**: SHA-256 hash of file contents (for text files under 10MB)
- **Modification Time**: File's last modification timestamp
- **File Size**: Size of the file in bytes
- **Indexing Time**: When the file was last indexed

This metadata is stored in a state file at `.files-db-mcp/file_processor_state.json` in the data directory.

### Change Detection

On startup or during reindexing, Files-DB-MCP:

1. Scans the project directory for all files
2. Compares the list of files with previously indexed files
3. Detects deleted files and removes them from the index
4. Checks each file's current metadata against stored metadata
5. Only reindexes files whose content hash, size, or modification time has changed

### Live File Monitoring

In addition to incremental indexing at startup, Files-DB-MCP continuously monitors file system changes using the file watcher component. This ensures that:

- New files are automatically indexed
- Modified files are reindexed
- Deleted files are removed from the index

## Configuration

### Command Line Options

The following command line options control indexing behavior:

```bash
# Force a full reindex instead of using incremental indexing
--force-reindex

# Set the data directory where the state file is stored
--data-dir /path/to/data
```

### Docker Environment Variables

When using Docker, you can set these environment variables:

```
FORCE_REINDEX=true  # Force a full reindex instead of incremental
```

## MCP Interface

The MCP interface provides two functions for controlling indexing:

1. **trigger_reindex**: Start a new indexing process
   ```json
   {
     "function": "trigger_reindex",
     "parameters": {
       "incremental": true  // Set to false for full reindex
     }
   }
   ```

2. **get_indexing_status**: Check the current indexing status
   ```json
   {
     "function": "get_indexing_status",
     "parameters": {}
   }
   ```

### Example Response

```json
{
  "success": true,
  "is_complete": true,
  "progress": 100.0,
  "files_indexed": 247,
  "total_files": 247
}
```

## Performance Considerations

Incremental indexing provides significant performance benefits:

| Scenario | Full Indexing | Incremental Indexing |
|----------|---------------|----------------------|
| First run | 100% (baseline) | Same as full indexing |
| No changes | 100% | ~5% (only scanning) |
| Few changes (1-5 files) | 100% | ~10-15% |
| Many changes (10-20% of files) | 100% | ~25-30% |

## Limitations

- Binary files over 10MB use modification time and size instead of content hashes
- Temporary files created and deleted between indexing runs might not be detected
- Rapid, frequent changes to many files can cause increased I/O load

## Troubleshooting

### Reset Indexing State

If you need to reset the indexing state and force a full reindex:

1. Stop the Files-DB-MCP service
2. Delete the state file at `.files-db-mcp/file_processor_state.json`
3. Restart with the `--force-reindex` flag

### Debugging Incremental Indexing

To see detailed logs about which files are being processed during incremental indexing, enable debug mode:

```bash
--debug
```

This will show:
- Files that were detected as changed
- Files that were deleted
- The reason a file was considered changed (hash mismatch, size change, etc.)
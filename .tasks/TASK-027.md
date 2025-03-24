# TASK-027: Improve startup progress indication

## Priority: High

## Status: To Do

## Description
Currently, when starting files-db-mcp for the first time, the user sees a series of periods/dots for an extended time without any clear indication of what's happening or how long it will take. The service is downloading large model files (~300-500MB) but the user has no visibility into this process.

## Requirements
- Show clear progress indication during model download phase
- Display download speeds and estimated time remaining
- Show which specific model files are being downloaded
- Provide a summary of total download size and progress percentage
- Ensure this information is visible in both the Docker logs and the startup script output

## Implementation Details
1. Modify `vector_search.py` to expose download progress events
2. Capture and forward Hugging Face model download progress
3. Add a progress bar similar to the one shown during file indexing
4. Update the run.sh script to display this information during startup
5. Consider adding a new health check endpoint that returns download status

## Acceptance Criteria
- Users can see clear progress indication during first startup
- Progress shows: which model is downloading, percentage complete, speed, ETA
- Information is consistently visible in logs and console output
- Startup script properly relays this information to the user

## Related Files
- `/src/vector_search.py`
- `/run.sh` 
- `/src/main.py`

## Notes
Model download occurs in the vector_search.py file when initializing the SentenceTransformer model. We need to capture the progress callbacks from HuggingFace and expose them through our health endpoint.
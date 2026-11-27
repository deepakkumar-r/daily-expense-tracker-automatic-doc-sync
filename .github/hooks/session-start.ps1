$context = @{
    systemMessage = "Agentic SDLC active: use the Orchestrator, preserve US-001, and keep requirements/design decisions human-approved."
}
$context | ConvertTo-Json -Compress

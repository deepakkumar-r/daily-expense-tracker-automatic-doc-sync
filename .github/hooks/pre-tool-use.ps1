$raw = [Console]::In.ReadToEnd()
$event = $null
if ($raw) {
    try { $event = $raw | ConvertFrom-Json } catch {}
}
$toolName = [string]$event.toolName
$readOnly = @("read", "search", "list", "get", "view", "rg", "glob")
if ($readOnly | Where-Object { $toolName -like "$_*" }) {
    @{ hookSpecificOutput = @{ hookEventName = "PreToolUse"; permissionDecision = "allow" } } | ConvertTo-Json -Compress
} else {
    @{
        hookSpecificOutput = @{
            hookEventName = "PreToolUse"
            permissionDecision = "ask"
            permissionDecisionReason = "Human approval is required before changing files, running commands, or publishing."
        }
    } | ConvertTo-Json -Compress
}

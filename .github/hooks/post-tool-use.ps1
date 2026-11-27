$changed = @(git diff --name-status 2>$null)
$sourcePatterns = @("src/", "tests/", ".github/agents/", ".github/instructions/", ".github/prompts/", ".github/skills/")
$sourceChanged = @($changed | Where-Object {
    $path = ($_ -split "`t")[-1]
    $sourcePatterns | Where-Object { $path.StartsWith($_, [System.StringComparison]::OrdinalIgnoreCase) }
})
$summary = if ($changed.Count -gt 0) { "Changed files detected:`n$($changed -join "`n")" } else { "No working-tree changes detected." }
if ($sourceChanged.Count -gt 0) {
    $summary += "`nSource or workflow changes may affect documentation."
    $summary += "`nMANDATORY HUMAN GATE: ask the user Yes/No before editing corresponding docs."
}
@{
    continue = $true
    systemMessage = "$summary`nUse local Documentation Sync for affected Markdown only; do not wait for GitHub Actions."
} | ConvertTo-Json -Compress



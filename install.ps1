# Copy the tutor skills into ~/.claude/skills so they run as /learn, /hint, ...
# Existing skills with the same name are skipped unless -Force is given.
param([switch]$Force)

$src = Join-Path $PSScriptRoot "skills"
$dst = Join-Path $HOME ".claude\skills"
New-Item -ItemType Directory -Force $dst | Out-Null

foreach ($skill in Get-ChildItem $src -Directory) {
    $target = Join-Path $dst $skill.Name
    if ((Test-Path $target) -and -not $Force) {
        Write-Host "skip  $($skill.Name) (already exists; rerun with -Force to overwrite)"
        continue
    }
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse $skill.FullName $target
    Write-Host "ok    $($skill.Name)"
}
Write-Host "Done. Restart Claude Code, then type /learn."

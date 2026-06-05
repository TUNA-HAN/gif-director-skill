[CmdletBinding()]
param(
    [string[]]$Agent = @("all"),
    [ValidateSet("user", "project")]
    [string]$Scope = "user",
    [string]$Repo = "TUNA-HAN/gif-director-skill",
    [string]$Skill = "gif-director",
    [string]$Pin = "",
    [switch]$Check,
    [switch]$UpdateOnly,
    [switch]$PrintOnly
)

$ErrorActionPreference = "Stop"

$SupportedAgents = @("codex", "claude-code", "antigravity")

function ConvertTo-DisplayCommand {
    param([string[]]$Arguments)

    $parts = foreach ($item in $Arguments) {
        if ($item -match "\s") {
            '"' + ($item -replace '"', '\"') + '"'
        } else {
            $item
        }
    }
    return "gh " + ($parts -join " ")
}

function Resolve-AgentList {
    param([string[]]$RequestedAgents)

    $expanded = New-Object System.Collections.Generic.List[string]
    foreach ($entry in $RequestedAgents) {
        foreach ($agentName in ($entry -split ",")) {
            $clean = $agentName.Trim().ToLowerInvariant()
            if ($clean.Length -eq 0) {
                continue
            }
            if ($clean -eq "all") {
                foreach ($supported in $SupportedAgents) {
                    if (-not $expanded.Contains($supported)) {
                        $expanded.Add($supported)
                    }
                }
                continue
            }
            if ($SupportedAgents -notcontains $clean) {
                throw "Unsupported agent '$agentName'. Supported values: all, $($SupportedAgents -join ', ')"
            }
            if (-not $expanded.Contains($clean)) {
                $expanded.Add($clean)
            }
        }
    }

    if ($expanded.Count -eq 0) {
        throw "No agents selected."
    }
    return $expanded.ToArray()
}

function Invoke-GhSkillCommand {
    param([string[]]$Arguments)

    $commandLine = ConvertTo-DisplayCommand -Arguments $Arguments
    if ($PrintOnly) {
        Write-Output $commandLine
        return
    }

    Write-Output $commandLine
    & gh @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $commandLine"
    }
}

if (-not $PrintOnly -and -not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI 'gh' was not found. Install it from https://cli.github.com/ and authenticate if needed."
}

if ($Check) {
    Invoke-GhSkillCommand -Arguments @("skill", "update", "--dry-run", $Skill)
    return
}

if ($UpdateOnly) {
    Invoke-GhSkillCommand -Arguments @("skill", "update", $Skill, "--all")
    return
}

$agents = Resolve-AgentList -RequestedAgents $Agent
foreach ($agentName in $agents) {
    $arguments = @("skill", "install", $Repo, $Skill, "--agent", $agentName, "--scope", $Scope, "--force")
    if ($Pin.Trim().Length -gt 0) {
        $arguments += @("--pin", $Pin.Trim())
    }
    Invoke-GhSkillCommand -Arguments $arguments
}

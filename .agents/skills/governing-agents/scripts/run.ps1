<#
.SYNOPSIS
仓库维护命令的 Windows 入口。

.DESCRIPTION
只读取仓库根目录 config.toml 的 python 字段，验证指定解释器后执行同目录的 run.py。
不从 PATH、环境变量或其他运行时配置选择 Python。
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Arguments
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$configPath = Join-Path $root 'config.toml'
$runnerPath = Join-Path $PSScriptRoot 'run.py'

$python = $null
foreach ($line in Get-Content -LiteralPath $configPath -Encoding UTF8) {
    if ($line -match '^\s*python\s*=\s*"([^"]+)"\s*(#.*)?$') {
        $python = $Matches[1]
        break
    }
}

if ([string]::IsNullOrWhiteSpace($python) -or -not (Test-Path -LiteralPath $python -PathType Leaf)) {
    Write-Error "config.toml python is missing or not executable: $python; fix the root config.toml."
    exit 1
}

$versionText = & $python -c 'import sys; print(sys.version_info[0], sys.version_info[1], sep=chr(46))' 2>$null
if ($LASTEXITCODE -ne 0 -or $versionText -notmatch '^3\.(\d+)$' -or [int]$Matches[1] -lt 12) {
    Write-Error "config.toml python must point to Python >= 3.12: $python"
    exit 1
}

& $python $runnerPath @Arguments
exit $LASTEXITCODE

# NexusVI — reproducible baseline audit

Status: initial audit; no runtime changes and no independent Windows/GPU results yet.
Upstream: XCL (GPL-2.0-only). Preserve the upstream history, credits and license.
Baseline: `83b008188efbf954b846667f48d75e3fa9310a01` on the original fork's main.

## First milestone: validate the inherited runtime

Use the repository's own synthetic test title and fixtures. Do not obtain or use leaked
game files, SDK material, keys or DRM circumvention. Do not upload private logs or binaries.

Requirements are documented in the upstream README: Windows 10/11 x64, stable MSVC Rust,
Windows SDK and a D3D12 adapter supporting SM 6.6 and mesh shaders. Some tests also need
Gaming Services and DXC. Follow the upstream instructions for those components.

On a Windows PC with Git, the prerequisites and PowerShell, run:

```powershell
git clone https://github.com/Rogeriomatador/NexusVI.git
cd NexusVI
git switch --detach 83b008188efbf954b846667f48d75e3fa9310a01
git status --short
git rev-parse HEAD
rustc -Vv
cargo -V
Get-CimInstance Win32_Processor | Select-Object Name
Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,BuildNumber
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
.\scripts\test.ps1
```

Run in a fresh shell with no XCL_SAMPLE_* variables set; tests requiring retail data are
outside this baseline. Record the actual pass/fail/ignore totals for all test binaries and
GPU skip reasons separately. An unavailable GPU test is not a verified pass. Review any
output for personal paths or identifiers before sharing. Do not claim compatibility with
a commercial title based on the synthetic suite.

## Avoid duplicating upstream work

The upstream PRs #2887 (cold/warm performance runner), #2888 (artifact comparison), and
#2959 (benchmark regression thresholds) were open at the initial audit. They overlap with
the proposed measurement tooling. Review their current status before implementing a new
comparator. The first candidate change should address a demonstrated failure on the
synthetic test workload, with a failing-before/passing-after regression test.

## Acceptance

1. Record the clean commit, Windows build, GPU/driver, CPU, RAM and Rust/DXC versions.
2. Build and execute the full test suite; report skips, failures and actual counts.
3. Identify one reproducible issue, check upstream issues/PRs for duplicates, and isolate
   the smallest fix on a separate branch.
4. Run the same tests again, without silently changing hardware or settings.
5. Report the measurements and limitations; no invented percentages or FPS claims.

AI assistance: ChatGPT (GPT-6.2), initial repository audit and this protocol.
No Windows/GPU test results have been generated as part of this document.

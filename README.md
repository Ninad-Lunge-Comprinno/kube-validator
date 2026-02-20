# kube-validator

CLI tool to validate whether key EKS cluster best-practice components are installed.

[![Demo](https://img.youtube.com/vi/5NOonU0VCCs/0.jpg)](https://www.youtube.com/watch?v=5NOonU0VCCs)


## What it checks by default

- Metrics Server
- Cluster Autoscaler (or Karpenter as alternative)
- EBS CSI Driver controller and node daemonset
- Amazon VPC CNI (`aws-node`)
- CoreDNS
- kube-proxy

For components that are commonly deployed outside `kube-system` (for example Metrics Server or Cluster Autoscaler), checks scan all namespaces.

## CLI commands

Run scan (default command):

```bash
python3 kube_validator.py
```

Explicit scan subcommand:

```bash
python3 kube_validator.py scan
python3 -m kubeval scan
```

List built-in checks:

```bash
python3 kube_validator.py list-checks
python3 -m kubeval list-checks
```

Interactive executable wizard (recommended):

```bash
./kubevalctl
```

This flow prompts for:
- AWS region
- EKS cluster name
- Optional AWS profile
- Optional custom checks file
- Output format

It then:
- Validates AWS credentials (`aws sts get-caller-identity`)
- Prompts to run `aws configure` if credentials are missing/invalid
- Runs `aws eks update-kubeconfig`
- Executes the cluster scan

## Prerequisites

- `kubectl` installed and configured
- `aws` CLI installed and configured (wizard can guide configuration)
- Access to your EKS cluster (`kubectl get nodes` should work)
- Python 3.9+

Use specific context:

```bash
python3 kube_validator.py scan --context my-eks-context
```

Output as JSON:

```bash
python3 kube_validator.py scan --output json
```

Include custom checks:

```bash
python3 kube_validator.py scan --checks-file checks.example.json
```

Disable pixel-style startup banner:

```bash
python3 kube_validator.py scan --no-banner
```

Disable retro scan spinner animation:

```bash
python3 kube_validator.py scan --no-spinner
```

## Custom checks format

Provide a JSON file:

```json
{
  "checks": [
    {
      "id": "aws-load-balancer-controller",
      "title": "AWS Load Balancer Controller installed",
      "resource": "deployment",
      "namespace": "kube-system",
      "match_type": "contains",
      "match_value": "aws-load-balancer-controller",
      "min_count": 1
    }
  ]
}
```

`match_type` options:

- `exact`
- `contains`
- `regex`

## Exit codes

- `0`: all checks passed
- `1`: one or more checks failed or errored
- `2`: usage/setup error (for example kubectl unavailable, invalid checks file)

## Project structure

- `kubeval/cli.py`: command entrypoint and orchestration
- `kubeval/domain/`: domain models and shared constants
- `kubeval/application/`: use-cases and check execution logic
- `kubeval/infrastructure/`: external adapters (for example kubectl client)
- `kubeval/presentation/`: output/rendering layers
- `kubeval/checks/`: check catalog, loader, and policies
- `kubeval/checks/builtin/`: built-in checks (one folder per check with `check.json`)
- `kubeval/kubectl.py`, `kubeval/engine.py`, `kubeval/models.py`, `kubeval/reporting.py`: backward-compatible shims to new layered modules
- `kubeval/banner.py`: pixel-style startup text
- `kube_validator.py`: compatibility wrapper

## Documentation

- `docs/ARCHITECTURE.md`: detailed explanation of code flow, module responsibilities, and extension patterns

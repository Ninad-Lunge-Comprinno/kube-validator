# kube-validator Flow Diagram

This diagram captures the two main user entry paths:

- `./kubevalctl`: interactive wizard for AWS/EKS setup plus scan
- `python3 kube_validator.py` or `python3 -m kubeval`: direct CLI scan/list flow

## Overall application flow

```mermaid
flowchart TD
    A[User starts application] --> B{Entry point}

    B -->|./kubevalctl| C[Print banner and wizard intro]
    B -->|python3 kube_validator.py\npython3 -m kubeval| D[kubeval.__main__ -> kubeval.cli.main]

    C --> E{aws and kubectl present?}
    E -->|No| Z1[Exit 2: setup error]
    E -->|Yes| F[Prompt for region, cluster, profile,\nchecks file, output]
    F --> G[aws sts get-caller-identity]
    G --> H{Credentials valid?}
    H -->|No| I{Run aws configure?}
    I -->|No| Z1
    I -->|Yes| J[Run aws configure and re-check]
    J --> K{Credentials valid now?}
    K -->|No| Z1
    K -->|Yes| L[aws eks update-kubeconfig]
    H -->|Yes| L
    L --> M{Kubeconfig updated?}
    M -->|No| Z1
    M -->|Yes| N[Invoke kubeval.cli.main scan argv]

    D --> O{Command}
    O -->|scan or default| P[_command_scan]
    O -->|list-checks| Q[_command_list_checks]

    N --> P

    Q --> R[Load built-in checks]
    R --> S{Output format}
    S -->|table| T[Print banner and checks catalog]
    S -->|json| U[Emit checks payload as JSON]
    T --> Z0[Exit 0]
    U --> Z0

    P --> V[Create KubectlClient]
    V --> W[Validate kubectl availability/usability]
    W --> X{Validation passed?}
    X -->|No| Z1
    X -->|Yes| Y[Load built-in checks]
    Y --> AA{--checks-file provided?}
    AA -->|Yes| AB[Load and validate custom checks JSON]
    AA -->|No| AC[Use built-in checks only]
    AB --> AD{Checks file valid?}
    AD -->|No| Z1
    AD -->|Yes| AE[Combine checks]
    AC --> AE
    AE --> AF{table + tty + spinner enabled?}
    AF -->|Yes| AG[Run checks with per-check spinner]
    AF -->|No| AH[Run checks directly]
    AG --> AI[Apply autoscaling coverage policy]
    AH --> AI
    AI --> AJ[Summarize PASS/FAIL/ERROR]
    AJ --> AK{Output format}
    AK -->|table| AL[Optional banner + results table + summary note]
    AK -->|json| AM[Emit results payload as JSON]
    AL --> AN{Any FAIL or ERROR?}
    AM --> AN
    AN -->|Yes| Z2[Exit 1]
    AN -->|No| Z0
```

## Scan execution detail

```mermaid
flowchart LR
    A[ResourceCheck list] --> B[Run checks or spinner loop]
    B --> C[Run single resource check]
    C --> D[Fetch resources through KubectlClient]
    D --> E[Build kubectl get command with json output]
    E --> F[Execute kubectl subprocess]
    F --> G{Command ok?}
    G -->|No| H[Return CheckResult ERROR]
    G -->|Yes| I[Parse items from kubectl JSON]
    I --> J[Match resource names by exact contains or regex rules]
    J --> K{Enough matches found?}
    K -->|Yes| L[Return CheckResult PASS]
    K -->|No| M[Return CheckResult FAIL]
    H --> N[Collect result]
    L --> N
    M --> N
    N --> O[Apply autoscaling coverage policy]
    O --> P[Build summary]
    P --> Q[Render table or json output]
```

from __future__ import annotations

import json
import shutil
import subprocess

from kubeval.domain.models import ResourceRef


class KubectlClient:
    def __init__(self, context: str | None = None, timeout_seconds: int = 15) -> None:
        self.context = context
        self.timeout_seconds = timeout_seconds

    def validate(self) -> str | None:
        if shutil.which("kubectl") is None:
            return "kubectl is not installed or not in PATH"

        stdout, err = self.run_command(["kubectl", "version", "--client", "-o", "json"])
        if err:
            return f"kubectl is not usable: {err}"
        try:
            client_version = json.loads(stdout or "{}").get("clientVersion", {})
            version = client_version.get("gitVersion", "unknown")
        except json.JSONDecodeError:
            version = "unknown"
        return None if version else "Unable to read kubectl version"

    def run_command(self, cmd: list[str]) -> tuple[str | None, str | None]:
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return None, f"Command timed out: {' '.join(cmd)}"
        except Exception as exc:  # pragma: no cover
            return None, str(exc)

        if proc.returncode != 0:
            stderr = proc.stderr.strip() or proc.stdout.strip() or "unknown kubectl error"
            return None, stderr
        return proc.stdout, None

    def get_resources(
        self,
        resource: str,
        namespace: str | None,
    ) -> tuple[list[ResourceRef], str | None]:
        cmd = ["kubectl"]
        if self.context:
            cmd += ["--context", self.context]
        cmd += ["get", resource]
        if namespace:
            cmd += ["-n", namespace]
        else:
            cmd += ["-A"]
        cmd += ["-o", "json"]

        stdout, err = self.run_command(cmd)
        if err:
            return [], err

        try:
            data = json.loads(stdout or "{}")
        except json.JSONDecodeError:
            return [], "kubectl returned non-JSON output"

        resources: list[ResourceRef] = []
        for item in data.get("items", []):
            metadata = item.get("metadata", {})
            name = metadata.get("name", "")
            ns = metadata.get("namespace", namespace or "default")
            if name:
                resources.append(ResourceRef(name=name, namespace=ns))
        return resources, None

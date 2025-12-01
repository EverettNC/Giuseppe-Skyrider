# dependency_shield.py
import pkg_resources
from packaging.requirements import Requirement
from packaging.version import Version
import subprocess
import json
import os
from pathlib import Path

SHIELD_LOCK = Path("dependency_shield.lock.json")

KNOWN_BREAKERS = {
    "thinc": {"numpy": "<1.24.0"},           # thinc 8.2+ hates numpy 2.x
    "torch": {"numpy": "<2.0.0"},            # torch 2.3+ still fragile with numpy 2
    "spacy": {"thinc": ">=8.2.0,<8.3.0"},    # spacy pins thinc hard
}

def scan_and_shield():
    installed = {d.project_name: d.version for d in pkg_resources.working_set}
    conflicts = []

    for pkg, constraints in KNOWN_BREAKERS.items():
        if pkg not in installed:
            continue
        for dep, version_spec in constraints.items():
            if dep in installed:
                req = Requirement(f"{dep}{version_spec}")
                if not req.specifier.contains(Version(installed[dep])):
                    conflicts.append((pkg, installed[pkg], dep, installed[dep], str(req.specifier)))

    if conflicts:
        print("🚨 DEPENDENCY SHIELD ACTIVATED")
        for pkg, pkg_ver, dep, dep_ver, spec in conflicts:
            print(f"  {pkg} {pkg_ver} breaks {dep} {dep_ver} — needs {spec}")
        
        # Auto-patch pip constraints
        constraints_file = Path("constraints.txt")
        with constraints_file.open("a") as f:
            for _, _, dep, _, spec in conflicts:
                f.write(f"\n{dep}{spec}")
        print(f"  → Patched {constraints_file}")

        # Update lockfile
        SHIELD_LOCK.write_text(json.dumps({
            "blocked_at": str(__import__("datetime").datetime.now()),
            "conflicts": conflicts
        }, indent=2))

        print("Shield complete. Run with --constraint constraints.txt to stay safe.")
    else:
        print("DependencyShield: All clear. Fleet is stable.")

if __name__ == "__main__":
    scan_and_shield()


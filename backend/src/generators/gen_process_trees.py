"""
Process Tree Generator for CyberDemo.

Generates realistic process tree data showing parent-child process relationships
for EDR detections. Creates realistic attack chains showing how malicious
processes spawn from legitimate parent processes.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .constants import PROCESS_CHAINS, MALICIOUS_FILENAMES


def _generate_pid(rng: random.Random) -> int:
    """Generate a realistic process ID."""
    return rng.randint(100, 65535)


def _generate_process_start_time(
    rng: random.Random,
    base_time: Optional[datetime] = None
) -> str:
    """Generate a process start time."""
    if base_time is None:
        base_time = datetime.now()
    # Process starts within 1 hour before detection
    offset = rng.randint(0, 3600)
    start_time = base_time - timedelta(seconds=offset)
    return start_time.isoformat()


def _get_process_path(process_name: str, rng: random.Random) -> str:
    """Get the typical path for a process."""
    system_processes = {
        "explorer.exe": "C:\\Windows\\explorer.exe",
        "cmd.exe": "C:\\Windows\\System32\\cmd.exe",
        "powershell.exe": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
        "services.exe": "C:\\Windows\\System32\\services.exe",
        "svchost.exe": "C:\\Windows\\System32\\svchost.exe",
        "winlogon.exe": "C:\\Windows\\System32\\winlogon.exe",
        "userinit.exe": "C:\\Windows\\System32\\userinit.exe",
        "wmiprvse.exe": "C:\\Windows\\System32\\wbem\\wmiprvse.exe",
        "wmic.exe": "C:\\Windows\\System32\\wbem\\wmic.exe",
        "mshta.exe": "C:\\Windows\\System32\\mshta.exe",
        "wscript.exe": "C:\\Windows\\System32\\wscript.exe",
        "certutil.exe": "C:\\Windows\\System32\\certutil.exe",
        "outlook.exe": "C:\\Program Files\\Microsoft Office\\root\\Office16\\outlook.exe",
        "winword.exe": "C:\\Program Files\\Microsoft Office\\root\\Office16\\winword.exe",
        "excel.exe": "C:\\Program Files\\Microsoft Office\\root\\Office16\\excel.exe",
        "chrome.exe": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    }

    if process_name in system_processes:
        return system_processes[process_name]

    # Unknown process - likely malware
    if process_name in MALICIOUS_FILENAMES:
        return f"C:\\Users\\user\\AppData\\Local\\Temp\\{process_name}"

    return f"C:\\Windows\\System32\\{process_name}"


def _generate_process_cmdline(process_name: str, rng: random.Random) -> str:
    """Generate a command line for a process."""
    cmdlines = {
        "explorer.exe": "C:\\Windows\\explorer.exe",
        "cmd.exe": "cmd.exe /c",
        "powershell.exe": "powershell.exe -NoP -NonI -W Hidden",
        "services.exe": "C:\\Windows\\System32\\services.exe",
        "svchost.exe": "C:\\Windows\\System32\\svchost.exe -k netsvcs",
        "winlogon.exe": "winlogon.exe",
        "userinit.exe": "C:\\Windows\\System32\\userinit.exe",
        "wmiprvse.exe": "C:\\Windows\\System32\\wbem\\wmiprvse.exe",
        "wmic.exe": "wmic.exe process call create",
        "mshta.exe": "mshta.exe vbscript:Execute",
        "wscript.exe": "wscript.exe //B //E:jscript",
        "certutil.exe": "certutil.exe -urlcache -split -f",
        "outlook.exe": "\"C:\\Program Files\\Microsoft Office\\root\\Office16\\outlook.exe\"",
        "winword.exe": "\"C:\\Program Files\\Microsoft Office\\root\\Office16\\winword.exe\" /n",
        "excel.exe": "\"C:\\Program Files\\Microsoft Office\\root\\Office16\\excel.exe\" /e",
        "chrome.exe": "\"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --type=renderer",
    }

    return cmdlines.get(process_name, process_name)


def _build_process_node(
    process_name: str,
    rng: random.Random,
    parent_pid: Optional[int] = None,
    depth: int = 0,
    base_time: Optional[datetime] = None
) -> Dict:
    """Build a single process node."""
    pid = _generate_pid(rng)

    return {
        "process_name": process_name,
        "process_id": pid,
        "parent_process_id": parent_pid,
        "process_path": _get_process_path(process_name, rng),
        "cmdline": _generate_process_cmdline(process_name, rng),
        "start_time": _generate_process_start_time(rng, base_time),
        "user": f"CORP\\user{rng.randint(1, 100):03d}",
        "depth": depth,
    }


def _select_process_chain(rng: random.Random) -> List[str]:
    """Select a process chain template."""
    base_chain = rng.choice(PROCESS_CHAINS)

    # Sometimes add additional malicious processes at the end
    if rng.random() < 0.3:
        malware_name = rng.choice(MALICIOUS_FILENAMES)
        return base_chain + [malware_name]

    return base_chain[:]


def _build_process_tree(
    detection_id: str,
    rng: random.Random,
    base_time: Optional[datetime] = None
) -> Dict:
    """Build a complete process tree for a detection."""
    chain = _select_process_chain(rng)

    # Build the tree structure
    root_process = None
    children = []
    current_parent_pid = None

    for depth, process_name in enumerate(chain):
        node = _build_process_node(
            process_name=process_name,
            rng=rng,
            parent_pid=current_parent_pid,
            depth=depth,
            base_time=base_time,
        )

        if depth == 0:
            root_process = node
        else:
            children.append(node)

        current_parent_pid = node["process_id"]

    return {
        "tree_id": f"TREE-{uuid.UUID(int=rng.getrandbits(128))}",
        "detection_id": detection_id,
        "root_process": root_process,
        "children": children,
        "depth": len(chain),
    }


def generate_process_trees(
    detections: List[Dict],
    seed: int = 42
) -> List[Dict]:
    """
    Generate process trees for EDR detections.

    Args:
        detections: List of detection dictionaries from gen_edr
        seed: Random seed for reproducibility (default 42)

    Returns:
        List of process tree dictionaries

    Example:
        >>> from gen_edr import generate_edr_detections
        >>> detections = generate_edr_detections(count=100, seed=42)
        >>> trees = generate_process_trees(detections, seed=42)
        >>> len(trees)
        100
        >>> trees[0].keys()
        dict_keys(['tree_id', 'detection_id', 'root_process', 'children', 'depth'])
    """
    rng = random.Random(seed)
    trees = []

    for detection in detections:
        detection_id = detection["detection_id"]

        # Parse timestamp if string
        timestamp = detection.get("timestamp")
        if isinstance(timestamp, str):
            try:
                base_time = datetime.fromisoformat(timestamp)
            except ValueError:
                base_time = datetime.now()
        else:
            base_time = datetime.now()

        tree = _build_process_tree(detection_id, rng, base_time)
        trees.append(tree)

    return trees


def get_tree_for_detection(
    trees: List[Dict],
    detection_id: str
) -> Optional[Dict]:
    """
    Get the process tree for a specific detection.

    Args:
        trees: List of process tree dictionaries
        detection_id: The detection ID to look up

    Returns:
        The process tree for the detection, or None if not found
    """
    for tree in trees:
        if tree["detection_id"] == detection_id:
            return tree
    return None


def get_deep_trees(
    trees: List[Dict],
    min_depth: int = 4
) -> List[Dict]:
    """
    Get process trees with depth >= min_depth.

    Args:
        trees: List of process tree dictionaries
        min_depth: Minimum depth threshold (default 4)

    Returns:
        List of trees meeting the depth criteria
    """
    return [t for t in trees if t.get("depth", 0) >= min_depth]


def get_tree_stats(trees: List[Dict]) -> Dict:
    """
    Get statistics about the process trees.

    Args:
        trees: List of process tree dictionaries

    Returns:
        Dictionary with tree statistics
    """
    if not trees:
        return {"count": 0}

    depths = [t.get("depth", 0) for t in trees]
    process_counts = [1 + len(t.get("children", [])) for t in trees]

    # Count unique root processes
    root_processes = {}
    for tree in trees:
        root = tree.get("root_process", {})
        name = root.get("process_name", "unknown")
        root_processes[name] = root_processes.get(name, 0) + 1

    return {
        "count": len(trees),
        "avg_depth": sum(depths) / len(depths),
        "max_depth": max(depths),
        "min_depth": min(depths),
        "avg_process_count": sum(process_counts) / len(process_counts),
        "root_process_distribution": root_processes,
    }


def flatten_tree(tree: Dict) -> List[Dict]:
    """
    Flatten a process tree into a list of processes.

    Args:
        tree: Process tree dictionary

    Returns:
        List of process dictionaries in execution order
    """
    processes = []

    root = tree.get("root_process")
    if root:
        processes.append(root)

    children = tree.get("children", [])
    processes.extend(children)

    return processes


if __name__ == "__main__":
    # Quick test
    import json

    # Create mock detections
    mock_detections = [
        {"detection_id": f"DET-{i:04d}", "timestamp": datetime.now().isoformat()}
        for i in range(10)
    ]

    trees = generate_process_trees(mock_detections, seed=42)

    print(f"Generated {len(trees)} process trees")

    stats = get_tree_stats(trees)
    print(f"\nTree statistics:")
    print(f"  Average depth: {stats['avg_depth']:.2f}")
    print(f"  Max depth: {stats['max_depth']}")
    print(f"  Average process count: {stats['avg_process_count']:.2f}")

    print("\nRoot process distribution:")
    for proc, count in stats["root_process_distribution"].items():
        print(f"  {proc}: {count}")

    print("\nSample tree:")
    print(json.dumps(trees[0], indent=2, default=str))

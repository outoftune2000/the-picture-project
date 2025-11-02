#!/usr/bin/env python
import os
import sys
from pathlib import Path


def main() -> None:
    # Ensure project root is on sys.path to import top-level 'service' package
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()



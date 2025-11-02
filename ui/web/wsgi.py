from __future__ import annotations

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Ensure project root is on sys.path to import top-level 'service'
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
application = get_wsgi_application()



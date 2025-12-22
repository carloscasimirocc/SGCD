#!/usr/bin/env python3
"""Simple script to create the Flask app, enter app context and verify
that SQLAlchemy mappers for Utilizador and HistoricoAlteracaoPerfil
are available. Prints errors/tracebacks to help debugging.

Run with:
r((venv) C:'\'Projecto'\'SGCD> python scripts'\'check_mappers.py)"""

import traceback
import sys
from pathlib import Path

# When you run a script located in a subdirectory (scripts/), Python sets
# sys.path[0] to that directory. That means imports like `import app` will
# fail unless the project root is on sys.path. Add the project root here so
# the script can be executed directly: `python scripts\check_mappers.py`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from app.app import create_app
except Exception as e:
    print('Failed importing create_app from app.app:')
    traceback.print_exc()
    # If the import failed due to a missing third-party package, provide
    # a helpful pip install hint using the missing module name.
    if isinstance(e, ModuleNotFoundError):
        missing = getattr(e, 'name', None)
        if missing:
            print('\nIt looks like the package "{}" is not installed.'.format(missing))
            print('Try installing dependencies in your venv, e.g.:')
            print('  python -m pip install {}\n'.format(missing))
    sys.exit(2)

app = None
try:
    app = create_app()
    print('create_app() OK')
except Exception:
    print('create_app() raised an exception:')
    traceback.print_exc()
    sys.exit(2)

with app.app_context():
    print('Entered app context')
    try:
        import app.historico.models as hm
        print('Imported app.historico.models OK')
    except Exception:
        print('Error importing app.historico.models:')
        traceback.print_exc()

    try:
        import app.utilizadores.models as um
        print('Imported app.utilizadores.models OK')
    except Exception:
        print('Error importing app.utilizadores.models:')
        traceback.print_exc()

    # Try to get SQLAlchemy mappers for both classes
    try:
        from sqlalchemy.orm import class_mapper
        class_mapper(um.Utilizador)
        class_mapper(hm.HistoricoAlteracaoPerfil)
        print('SQLAlchemy mappers available for Utilizador and HistoricoAlteracaoPerfil')
    except Exception:
        print('Mapper check failed:')
        traceback.print_exc()
        sys.exit(3)

print('Mapper check finished successfully')

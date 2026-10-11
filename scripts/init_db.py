"""Create or upgrade the database for the auth / acc / post structure.

Run from the project root:  python -m scripts.init_db

- Backs up the SQLite file first (app.db -> app.db.bak-<timestamp>).
- Drops tables whose columns no longer match the models, but ONLY if they are empty
  (create_all never alters an existing table, so stale tables would stay stale forever).
- Creates every missing table from the current models.
"""
import shutil
from datetime import datetime
from pathlib import Path

from sqlalchemy import inspect, text

from app.database import Base, engine
import app.acc.models  # noqa: F401  registers the models on Base
import app.auth.models  # noqa: F401
import app.post.models  # noqa: F401


def main() -> None:
    if engine.dialect.name == "sqlite" and engine.url.database:
        db_file = Path(engine.url.database)
        if db_file.exists() and db_file.stat().st_size > 0:
            backup = db_file.with_name(f"{db_file.name}.bak-{datetime.now():%Y%m%d-%H%M%S}")
            shutil.copy2(db_file, backup)
            print(f"Backed up {db_file} -> {backup}")

    inspector = inspect(engine)
    existing = set(inspector.get_table_names())

    with engine.begin() as conn:
        # Children before parents so foreign keys don't block the drop
        for table in reversed(Base.metadata.sorted_tables):
            if table.name not in existing:
                continue
            db_cols = {c["name"] for c in inspector.get_columns(table.name)}
            model_cols = {c.name for c in table.columns}
            if db_cols == model_cols:
                continue
            rows = conn.execute(text(f'SELECT COUNT(*) FROM "{table.name}"')).scalar()
            if rows:
                print(f"!! {table.name}: columns differ but it holds {rows} rows - left as is, migrate by hand")
                print(f"   missing in DB: {sorted(model_cols - db_cols)}  extra in DB: {sorted(db_cols - model_cols)}")
                continue
            conn.execute(text(f'DROP TABLE "{table.name}"'))
            print(f"Dropped stale empty table {table.name} (will be recreated)")

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    with engine.connect() as conn:
        for name in sorted(inspector.get_table_names()):
            rows = conn.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar()
            cols = ", ".join(c["name"] for c in inspector.get_columns(name))
            print(f"  {name:15} {rows:>4} rows  [{cols}]")
    print("Database ready.")


if __name__ == "__main__":
    main()

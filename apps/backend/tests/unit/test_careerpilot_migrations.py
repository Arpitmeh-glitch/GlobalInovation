import sqlite3

from app.db_engine import init_models_sync, make_sync_engine


def test_legacy_jobs_table_gets_additive_careerpilot_columns(tmp_path) -> None:
    database_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        CREATE TABLE jobs (
            job_id VARCHAR PRIMARY KEY,
            content TEXT NOT NULL,
            resume_id VARCHAR,
            created_at VARCHAR NOT NULL,
            metadata_json JSON NOT NULL
        )
        """
    )
    connection.execute(
        "INSERT INTO jobs (job_id, content, resume_id, created_at, metadata_json) VALUES (?, ?, ?, ?, ?)",
        ("legacy-job", "Legacy description", None, "2026-01-01T00:00:00+00:00", "{}"),
    )
    connection.commit()
    connection.close()

    engine = make_sync_engine(database_path)
    init_models_sync(engine)
    with engine.connect() as migrated:
        columns = {
            row[1] for row in migrated.exec_driver_sql("PRAGMA table_info(jobs)").all()
        }
        row = migrated.exec_driver_sql(
            "SELECT job_id, content FROM jobs WHERE job_id = 'legacy-job'"
        ).one()

    engine.dispose()
    assert {"provider", "title", "skills_required", "discovered_at"}.issubset(columns)
    assert row == ("legacy-job", "Legacy description")

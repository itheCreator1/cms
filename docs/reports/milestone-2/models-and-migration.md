# Milestone 2 Models and Migration

## Delivered

- `User`, `Article`, `Announcement`, `Page`, `Category`, `Tag`, and `Media` SQLAlchemy models.
- Article–tag association with a named composite primary key.
- Required role and content-status enums with stable PostgreSQL type names.
- Named primary-key, foreign-key, unique, check, and index conventions.
- Explicit indexes and uniqueness constraints for slug-backed resources.
- Restrictive foreign-key deletion behavior and relationships without content-deleting cascades.
- Werkzeug password-hash helpers on `User`.
- First reviewed Alembic revision: `739941d28772_add_cms_domain_models.py`.

## Migration review

The revision creates enum types before dependent tables, creates tables in dependency order, and reverses those operations during downgrade before explicitly dropping enum types. `Article.category_id` is required; featured media and state-dependent publication timestamps remain nullable.

No `db.create_all()` schema management is used.

## TDD and verification

The model contract first failed because models were not exported. Password behavior first failed because hash helpers did not exist. The PostgreSQL migration round trip first failed because there was no revision. Each was implemented after its expected RED result.

Final task verification reported:

```text
docker compose exec backend pytest -q backend/tests
28 passed in 1.98s

docker compose exec backend flask db check
No new upgrade operations detected.
```

Tests used temporary PostgreSQL databases and covered metadata, persistence/defaults, relationships, password hashing, uniqueness, delete restrictions, physical indexes/constraints/types, and upgrade/downgrade/re-upgrade behavior.

## Review and commit

Independent review found no substantive schema or migration defect. Documentation was intentionally handled in separate commits to preserve atomic history.

`590e4c9 feat(backend): add CMS domain schema`

# Database Migrations with Alembic

This project uses Alembic for database schema version control and migrations.

## Quick Start

### Run All Migrations
```bash
# From the backend/microservices/video_transcript_buddy_service directory
alembic upgrade head
```

### Check Current Version
```bash
alembic current
```

### View Migration History
```bash
alembic history --verbose
```

## Migration Files

- **0001_initial_schema.py** - Creates users, subscriptions, and usage_records tables
- **0002_add_transcripts_table.py** - Adds transcripts table with local/S3 storage support

## Creating New Migrations

### Auto-generate from Model Changes
```bash
alembic revision --autogenerate -m "description of changes"
```

### Create Empty Migration
```bash
alembic revision -m "description of changes"
```

## Common Commands

### Upgrade to Specific Version
```bash
alembic upgrade 0001  # Upgrade to version 0001
alembic upgrade +1    # Upgrade one version
```

### Downgrade
```bash
alembic downgrade -1  # Rollback one version
alembic downgrade base  # Rollback all
```

### Show SQL Without Executing
```bash
alembic upgrade head --sql
```

## Migration Workflow

1. **Make model changes** in `models/` directory
2. **Generate migration**: `alembic revision --autogenerate -m "description"`
3. **Review migration** in `alembic/versions/`
4. **Test migration**: `alembic upgrade head`
5. **Commit migration** file to version control

## Database Configuration

Database URL is configured in `alembic.ini`:
```ini
sqlalchemy.url = sqlite:///data/transcriptquery.db
```

For production, override with environment variable:
```bash
export DATABASE_URL="postgresql://user:pass@host/dbname"
alembic upgrade head
```

## Notes

- Always backup database before running migrations in production
- Test migrations on development/staging environments first
- Migration files are sequential and must be run in order
- Never modify migrations that have been deployed to production

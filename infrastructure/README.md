# Infrastructure Overview

This directory contains auxiliary assets for local orchestration and database migrations. Docker Compose bundles the API, worker, scheduler, Flower dashboard, PostgreSQL, Redis, and React frontend. Alembic migrations live under `backend/alembic/` and are executed via the provided `Makefile` targets.

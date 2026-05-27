# KR-4

## Setup

```bash
python -m pip install -r requirements.txt
```

## Task 9.1

```bash
cd kr-4/9-1
alembic upgrade head
python seed.py
uvicorn app:app --reload
```

## Task 10.1

```bash
cd kr-4/10-1
uvicorn app:app --reload
```

## Task 10.2

```bash
cd kr-4/10-2
uvicorn app:app --reload
```

## Task 11.1

```bash
cd kr-4/11-1
pytest
```

## Task 11.2

```bash
cd kr-4/11-2
pytest
```

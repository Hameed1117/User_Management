import asyncio
import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user_model import User, UserRole
from app.utils.security import hash_password
from app.main import app
from fastapi.testclient import TestClient
import uuid
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/myappdb")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    # Drop and create all tables before running the tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def user(db_session):
    fake = Faker()
    new_user = User(
        id=uuid.uuid4(),
        nickname=fake.user_name(),
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        role=UserRole.AUTHENTICATED,
        hashed_password=hash_password("MySuperPassword$1234"),
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    return new_user


@pytest_asyncio.fixture
async def verified_user(db_session):
    fake = Faker()
    user = User(
        id=uuid.uuid4(),
        nickname=fake.user_name(),
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        role=UserRole.AUTHENTICATED,
        hashed_password=hash_password("MySuperPassword$1234"),
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def locked_user(db_session):
    fake = Faker()
    user = User(
        id=uuid.uuid4(),
        nickname=fake.user_name(),
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        role=UserRole.AUTHENTICATED,
        hashed_password=hash_password("MySuperPassword$1234"),
        is_locked=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session):
    fake = Faker()
    user = User(
        id=uuid.uuid4(),
        nickname=fake.user_name(),
        email=fake.email(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        role=UserRole.ADMIN,
        hashed_password=hash_password("MySuperPassword$1234"),
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ✅ FIXED version to create 50 users with unique emails
@pytest_asyncio.fixture
async def users_with_same_role_50_users(db_session):
    """Create 50 users with AUTHENTICATED role without duplicate emails."""
    fake = Faker()
    users = []
    existing_emails = set()

    for _ in range(50):
        email = fake.email()
        while email in existing_emails:
            email = fake.email()
        existing_emails.add(email)

        user = User(
            id=uuid.uuid4(),
            nickname=fake.user_name(),
            email=email,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role=UserRole.AUTHENTICATED,
            hashed_password=hash_password("MySuperPassword$1234"),
        )
        db_session.add(user)
        users.append(user)

    await db_session.commit()
    return users

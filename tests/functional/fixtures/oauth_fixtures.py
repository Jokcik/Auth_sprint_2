from sqlalchemy.orm import Session
from services.user_service import UserService
from models.user import User

@pytest_asyncio.fixture
async def create_oauth_user(db: Session):
    user_service = UserService(db)
    oauth_user = User(
        username="oauthuser",
        email="oauthuser@example.com",
        oauth_provider="google",
        oauth_id="123456789"
    )
    db.add(oauth_user)
    db.commit()
    return oauth_user
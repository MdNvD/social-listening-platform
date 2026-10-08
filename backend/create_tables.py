from app.database.connection import Base, engine
from app.database.models import Search, Mention, MentionAnalysis


print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")
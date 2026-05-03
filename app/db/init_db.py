from app.db.database import Base,engine


def init_db():
    """
    Creates all tables in the database,
    Safe to run multiple times - uses CREATE TABLE IF NOT EXISTS
    """
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")


if __name__=="__main__":
    init_db()
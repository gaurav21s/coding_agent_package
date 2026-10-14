from sqlalchemy import create_engine, String, Integer, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# 1. Setup the engine for an in-memory SQLite database
engine = create_engine("sqlite:///:memory:", echo=False)

# 2. Define the Declarative Base
class Base(DeclarativeBase):
    pass

# 3. Define the Book model
class Book(Base):
    __tablename__ = "book"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    author: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"Book(id={self.id!r}, title={self.title!r}, author={self.author!r})"

# 4. Create the table
Base.metadata.create_all(engine)

# 5. Insert two books
with Session(engine) as session:
    book1 = Book(title="The Great Gatsby", author="F. Scott Fitzgerald")
    book2 = Book(title="1984", author="George Orwell")
    session.add_all([book1, book2])
    session.commit()

# 6. Fetch one book by its primary key
with Session(engine) as session:
    fetched_book = session.get(Book, 1)
    print(f"Fetched book: {fetched_book}")

    # 7. Run a raw SQL statement to count rows
    # We use the engine directly to execute raw SQL
    with engine.connect() as connection:
        result = connection.execute(text("SELECT count(*) FROM book"))
        count = result.scalar()
        print(f"Total row count (via raw SQL): {count}")

import sqlalchemy
from sqlalchemy import create_engine, String, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# 1. Define the Declarative Base
class Base(DeclarativeBase):
    pass

# 2. Define the Book model
class Book(Base):
    __tablename__ = "book"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    author: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"Book(id={self.id!r}, title={self.title!r}, author={self.author!r})"

def main():
    # 3. Create the engine (in-memory SQLite)
    engine = create_engine("sqlite:///:memory:")

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
        stmt = select(Book).where(Book.id == 1)
        fetched_book = session.scalar(stmt)
        print(f"Fetched Book: {fetched_book}")

    # 7. Run a raw SQL statement to count rows
    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM book"))
        count = result.scalar()
        print(f"Total Row Count (via raw SQL): {count}")

if __name__ == "__main__":
    main()

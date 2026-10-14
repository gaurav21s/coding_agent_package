from sqlalchemy import create_engine, String, Integer, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

                                                      
engine = create_engine("sqlite:///:memory:", echo=False)

                                
class Base(DeclarativeBase):
    pass

                          
class Book(Base):
    __tablename__ = "book"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    author: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"Book(id={self.id!r}, title={self.title!r}, author={self.author!r})"

                     
Base.metadata.create_all(engine)

                     
with Session(engine) as session:
    book1 = Book(title="The Great Gatsby", author="F. Scott Fitzgerald")
    book2 = Book(title="1984", author="George Orwell")
    session.add_all([book1, book2])
    session.commit()

                                      
with Session(engine) as session:
    fetched_book = session.get(Book, 1)
    print(f"Fetched book: {fetched_book}")

                                              
                                                   
    with engine.connect() as connection:
        result = connection.execute(text("SELECT count(*) FROM book"))
        count = result.scalar()
        print(f"Total row count (via raw SQL): {count}")

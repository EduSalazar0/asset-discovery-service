from infrastructure.database.connection import Base, engine
from worker.consumer import start_worker

if __name__ == "__main__":
    # Create DB tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Start the consumer worker
    start_worker()
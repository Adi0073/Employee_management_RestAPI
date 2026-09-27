from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    MONGO_URI:str=os.getenv("MONGO_DB_URI","mongodb://localhost:27017")
    MONGO_DB_NAME:str=os.getenv("MONGO_DB_NAME","Worksphere_DB")




import os
from dotenv import load_dotenv

# 自动加载 .env 文件
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

class Config:
    # Langfuse配置
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    USE_LANGFUSE = bool(LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY)
    
    # MySQL数据库配置
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "hr_agent")
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """构建SQLAlchemy数据库连接URI"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"

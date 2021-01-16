from dotenv import load_dotenv, find_dotenv
from os import getenv


load_dotenv(find_dotenv())

BLOG_READER_ACC = getenv('BLOG_READER_ACC')
BLOG_READER_PWD = getenv('BLOG_READER_PWD')

BLOG_WRITER_ACC = getenv('BLOG_WRITER_ACC')
BLOG_WRITER_PWD = getenv('BLOG_WRITER_PWD')

BLOG_DB = getenv('BLOG_DB')

SECRETS_WRITER_ACC = getenv('SECRETS_WRITER_ACC')
SECRETS_WRITER_PWD = getenv('SECRETS_WRITER_PWD')

SECRETS_READER_ACC = getenv('SECRETS_READER_ACC')
SECRETS_READER_PWD = getenv('SECRETS_READER_PWD')

SECRETS_DB = getenv('SECRETS_DB')

MONGO_HOST = getenv('MONGO_HOST')

LOGGING_COL = getenv('LOGGING_COL')




import os

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t", "yes", "on")

print(type(DEBUG), DEBUG)

from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
logger.add("logs/server.log", rotation="10 MB", compression="zip")

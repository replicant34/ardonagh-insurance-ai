import logging
import os


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def get_agent_logger():

    logger = logging.getLogger("insurance_ai")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, "agent.log")
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = get_agent_logger()
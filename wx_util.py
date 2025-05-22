def initLogging(scriptName: str, logFile="wx04849.log"):
    import logging
    from os import path

    logPath = path.join(path.dirname(path.abspath(__file__)), logFile)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        filename=logPath,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    logging.info(f"===== Starting {scriptName} =====")

    # Force flush to make sure it appears immediately
    for handler in logging.getLogger().handlers:
        handler.flush()

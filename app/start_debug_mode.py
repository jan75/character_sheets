import logging

from webapp import create_app

if __name__ == '__main__':
    # Logging configuration
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    logger.info('Creating flask application')

    app = create_app()
    app.run(debug=True, host='0.0.0.0')


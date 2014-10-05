FULL_VERSION = '1.9.12.post3'
VERSION = FULL_VERSION if FULL_VERSION.count('.') == 2 else \
    FULL_VERSION.rsplit('.', 1)[0]

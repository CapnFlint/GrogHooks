import logging

# API Configuration
host = ""
port = 0

log_file = "<log file>"
log_format = '%(asctime)s:%(levelname)s:%(message)s'
log_date_format = '%Y/%m/%d-%I:%M:%S'
log_level = logging.DEBUG

available_hooks = ['<some hook>']
# Secret key for verification
secret = ""

# Alert system websocket
ws_server = ""
websocket_secret = ""

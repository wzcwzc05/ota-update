from flask import Flask, request, send_from_directory
from multiprocessing import Process, Queue
import json
import os
import sys
import signal

app = Flask(__name__)


def signal_handler(sig, frame):
    sys.exit(0)


def http_server(update_queue):
    signal.signal(signal.SIGTERM, signal_handler)
    pass

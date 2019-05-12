# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
from threading import Condition
import threading
import time
from http import server
from fractions import Fraction

#resolution = (640, 480)
#resolution = (2592, 1944)
#resolution = (1296, 730)
#resolution = (1296, 972)

resolution = (2592/2, 200)
shutter_speed = 65759
awb_gains = (Fraction(139, 128), Fraction(227, 128))

awb_gains = (1, 1)

PAGE="""\
<html>
<head>
<title>Raspberry Pi - spectrometer</title>
</head>
<body>
<center><h1>Raspberry Pi - spectrometer </h1></center>
<center><img src="stream.mjpg"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

def printInfo(camera):
    print('iso: ', camera.iso)
    print('analog_gain: ', camera.analog_gain)
    print('digital_gain: ', camera.digital_gain)
    print('awb_gains: ', camera.awb_gains)
    print('awb_mode: ', camera.awb_mode)
    print('brightness: ', camera.brightness)
    print('clock_mode: ', camera.clock_mode)
    print('contrast: ', camera.contrast)
    print('drc_strength: ', camera.drc_strength)
    print('exposure_compensation: ', camera.exposure_compensation)
    print('exposure_mode: ', camera.exposure_mode)
    print('exposure_speed: ', camera.exposure_speed)
    print('framerate: ', camera.framerate)
    print('framerate_delta: ', camera.framerate_delta)
    print('framerate_range: ', camera.framerate_range)
    print('hflip: ', camera.hflip)
#    print('led: ', camera.led)
    print('sensor_mode: ', camera.sensor_mode)
    print('sharpness: ', camera.sharpness)
    print('shutter_speed: ', camera.shutter_speed)
    print('vflip: ', camera.vflip)
    print('video_denoise: ', camera.video_denoise)


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='%dx%d'%resolution , framerate=15) as camera:
    output = StreamingOutput()
    camera.iso = 800
    print('waiting for gain to settle')
    time.sleep(2)
    print('runing record')
    camera.exposure_mode = 'off'
    camera.shutter_speed = shutter_speed
    camera.awb_mode = 'off'
    camera.awb_gains = awb_gains
    camera.video_denoise = False
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
#        server.serve_forever()
        ServerThread = threading.Thread(target=server.serve_forever)
        ServerThread.start()
#        led = True
        while True:
            printInfo(camera)
            time.sleep(1)
#            camera.led = led
#            led = not led
    finally:
        camera.stop_recording()
        server.shutdown()

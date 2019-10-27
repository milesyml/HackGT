from flask import Flask, Response,render_template, request
import flask
import pyaudio
import wave
import time

import threading  

queue = []

class AsyncGitTask(threading.Thread):
  # def __init__(self, task_id=1, params=1):
  #     self.task_id = task_id
  #     self.params = params
  def run(self):
      ## Do processing
      ## store the result in table for id = self.task_id
      global is_recording
      is_recording = True
      CHUNK = 1024
      sampleRate = 44100
      bitsPerSample = 16
      channels = 2
      wav_header = genHeader(sampleRate, bitsPerSample, channels)

      stream = audio1.open(format=FORMAT, channels=CHANNELS,
                          rate=RATE, input=True,
                          frames_per_buffer=CHUNK)
      data = wav_header + stream.read(CHUNK)
      f = open('output.wav', 'ab')
      while is_recording:
          f.write(data)

          data = stream.read(CHUNK)

      f.close()

app = Flask(__name__)


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024

audio1 = pyaudio.PyAudio()

is_recording = False


def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

@app.route('/audio')
def audio():
   
    def sound():
        CHUNK = 1024
        sampleRate = 44100
        bitsPerSample = 16
        channels = 2
        wav_header = genHeader(sampleRate, bitsPerSample, channels)

        # stream = audio1.open(format=FORMAT, channels=CHANNELS,
        #                     rate=RATE, input=True,
        #                     frames_per_buffer=CHUNK)
        # data = wav_header + stream.read(CHUNK)
        # for i in range(10):
        #     while len(queue) == 0:
        #         pass
        #     queue.pop(0)

        while len(queue) == 0:
            pass

        data = wav_header + queue.pop(0)
        
        while True:
            if len(queue) == 0:
                continue
            yield (data)
            data = queue.pop(0)

    return Response(sound())

@app.route('/goLive')
def goLive():
    import requests

    # time.sleep(1)
    xml = "<play_info><app_key>CMwhZOwJsgUUclRmJ7k8dpv2KF2F8Qgr</app_key><url>http://192.168.1.15:5000/audio</url><service>service text</service><reason>reason text</reason><message>message text</message><volume>35</volume></play_info>"
    headers = {'Content-Type': 'application/xml'} # set what your server accepts
    requests.post('http://192.168.1.251:8090/speaker', data=xml, headers=headers)

@app.route('/live', methods=['POST'])
def live():
    # print("received audio")
    data = request.data
    # print(data)
    f = open('test.wav', 'wb')
    f.write(data)
    f.close()
    wf = wave.open('test.wav', 'rb')
    chunk = wf.readframes(wf.getnframes())
    wf.close()
    queue.append(data)
    return "ok"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/testtest.wav')
def get_recording():
    return flask.send_file("./test.wav")

@app.route('/ui')
def ui():
    # if request.url.startswith('http://'):
    #     url = request.url.replace('http://', 'https://', 1).replace("5000", "5001", 1)
    #     code = 301
    #     return flask.redirect(url, code=code)
    return render_template('ui.html')

@app.route('/start')
def start():
    print("starting")
    async_task = AsyncGitTask()
    async_task.start()
    return 'started'

@app.route('/stop')
def stop():
    print("stopping")
    global is_recording
    is_recording = False
    import soundfile as sf

    data, samplerate = sf.read('output.wav')
    sf.write('new_output.ogg', data, samplerate)

    return 'stopped'

@app.route('/send', methods=['POST'])
def send():
    print("received file")
    data = request.data
    f = open('test.wav', 'wb')
    f.write(data)
    f.close()
    return "okokokok"

@app.route('/send_text', methods=['POST'])
def send_text():
    print("received text")
    data = request.data
    print(data)


    # f = open('test.wav', 'wb')
    # f.write(data)
    # f.close()
    return "okokokok"

@app.route('/recording', methods=['POST'])
def recording():
    data = request.data
    print(data)

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(data))
    wf.close()

    return 'ok'


def http_app():
    app.run(host='0.0.0.0', debug=True, threaded=True, port=5000)

if __name__ == "__main__":
    # from multiprocessing import Process

    # Process(target=http_app, daemon=True).start()
    app.run(host='0.0.0.0', debug=True, threaded=True, port=5000)
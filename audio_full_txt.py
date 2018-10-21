import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from pydub import AudioSegment
from pydub.utils import make_chunks

import subprocess

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './gce.key'

def process_vid(vid_filepath, output_filepath):
    command = "ffmpeg -y -i " + vid_filepath + " -ar 16000 -vn resources/output.wav"
    subprocess.call(command, shell=True)

    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    file_name = os.path.join(
        os.path.dirname(__file__),
        'resources',
        'output.wav')

    myaudio = AudioSegment.from_file(file_name, "wav")
    audio = types.RecognitionAudio(content=myaudio.raw_data)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US')
    operation = client.long_running_recognize(config, audio)
    # [END speech_python_migration_async_request]

    print('Waiting for operation to complete...')
    response = operation.result(timeout=90)

    #Convert chunks to raw audio data which you can then feed to HTTP stream
    with open(output_filepath, 'w+') as outf:

        for result in response.results:
            outf.write(result.alternatives[0].transcript)
            outf.write(". ")

process_vid("resources/billgates.mp4", "resources/genesis.txt")
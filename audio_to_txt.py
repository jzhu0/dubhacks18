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
    chunk_length_ms = 30000 # pydub calculates in millisec
    chunks = make_chunks(myaudio, chunk_length_ms) #Make chunks of one sec

    #Convert chunks to raw audio data which you can then feed to HTTP stream
    with open(output_filepath, 'w+') as outf:
        for i, chunk in enumerate(chunks):
            print("chunk " + str(i) + " of " + str(len(chunks)-1))
            raw_audio_data = chunk.raw_data

            # Loads the audio into memory
            audio = types.RecognitionAudio(content=raw_audio_data)

            config = types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code='en-US')

            # Detects speech in the audio file
            response = client.recognize(config, audio)

            for result in response.results:
                outf.write(result.alternatives[0].transcript)
                outf.write(". ")

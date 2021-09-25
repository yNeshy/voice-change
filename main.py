# Math operations
import numpy as np

# Get requests to download mp3 or wav files
import requests

# Used to replace file operations with in memory operations (with ByteIO)
import io

# To read and write wav files
import soundfile
from copy import copy

# Imports related to the use of S3
import logging
import boto3
from botocore.exceptions import ClientError

# Convert MP3 files to WAV file
from pydub import AudioSegment


debug_url = 'https://file-examples-com.github.io/uploads/2017/11/file_example_WAV_1MG.wav'
debug_outputfile_noext = 'tobeuploaded'
debug_file = 'who-are-you.mp3'
BUCKET_NAME = ''


class AudioProcessing():
    def __init__(self, url=None, bytes_object=None, is_mp3=False):
        """
        In memory simple audio operation on wav files. Supports mp3 to wav conversion
        """
        if(url):
            # create wav file from url
            r = requests.get(url)
            bytes_object = r.content
        if(bytes_object.endswith(".mp3")):
            is_mp3 = True
        
        if(is_mp3):
            bytes_object = AudioProcessing.mp3_to_wav(bytes_object)
            print("Conversion successful")
        
        self.audio_data, self.freq = soundfile.read(bytes_object)
        return

    def write_to_file(self, filename):
        soundfile.write(filename, self.audio_data, self.freq)

    def write_to_ioBytes(self):
        output = io.BytesIO()
        soundfile.write(output, self.audio_data, self.freq, format='wav')
        return output

    def fetch_sound_wave(self ,url):
        r = requests.get(url)
        self.audio_data, self.freq = soundfile.read(io.BytesIO(r.content))

    def add_echo(self, delay):
        '''Applies an echo that is 0...<input audio duration in seconds> seconds from the beginning'''
        output_audio = copy(self.audio_data)
        output_delay = delay * self.freq

        for count in range(len(self.audio_data)):
            e = self.audio_data[count]
            output_audio[count] = e + self.audio_data[count - int(output_delay)]

        self.audio_data = output_audio

    def set_audio_speed(self, speed_factor):
        '''Sets the speed of the audio by a floating-point factor'''
        sound_index = np.round(np.arange(0, len(self.audio_data), speed_factor))
        self.audio_data = self.audio_data[sound_index[sound_index < len(self.audio_data)].astype(int)]

    def filter_frequency(self, threshold):
        output_audio = copy(self.audio_data)
        for count in range(len(self.audio_data)):
            e = self.audio_data[count]
            if ( e < threshold ):
                output_audio[count] = threshold
            else :
                output_audio[count] = e
        self.audio_data = output_audio

    def custom_filter(self, threshold):
        output_audio = copy(self.audio_data)
        for count in range(len(self.audio_data)):
            e = self.audio_data[count]
            output_audio[count] = (e / threshold)

        self.audio_data = output_audio

    def set_volume(self, level):
        '''Sets the overall volume of the data via floating-point factor'''
        output_audio = copy(self.audio_data)
        for count in range(len(self.audio_data)):
            e = self.audio_data[count]
            output_audio[count] = (e * level)

        self.audio_data = output_audio

    def deepen(self, factor=0.7):
        self.freq = int(self.freq * factor)

    def pitch(self, factor=0.7):
        self.freq = int(self.freq / factor)

    @staticmethod
    def hide_voice (audiotool):
        audiotool.set_volume(1.3)
        audiotool.add_echo(0.1)
        audiotool.custom_filter(1.3)
        audiotool.deepen()

    @staticmethod
    def mp3_to_wav(mp3):
        wav = io.BytesIO()
        sound = AudioSegment.from_mp3(mp3)
        sound.export(wav, format="wav")
        return wav

def fetch_from_url(url):
    r = requests.get(url)
    try:
        return io.BytesIO(r.content)
    except :
        raise(Exception("URL provided does not contain a wav file."))

def upload_file_to_S3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print("S3 error occured "+ e)
        return False
    return True

if __name__ == "__main__":
    audiotool = AudioProcessing(bytes_object="who-are-you.mp3", is_mp3=True)
    AudioProcessing.hide_voice(audiotool)
    output = audiotool.write_to_ioBytes()

    #upload_file_to_S3(output, BUCKET_NAME, object_name="modified_voice.wav")
    with open("result.wav", "wb") as f:
        f.write(output.getbuffer())
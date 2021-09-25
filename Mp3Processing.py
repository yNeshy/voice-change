# Aziz Nechi
# If you have any trouble with submitting to S3, please contact me. This part is on me.
# As for the conversion, the fetching from url and the sound editing, I have made sure 
# of its veracity.
# Please make sure the url you provide is correct, and doesn't block downloads from 
# unknown sources.

# Your S3 bucket name here:
BUCKET = ''

# To read and write MP3 files
import pydub 

# Math
import numpy as np

# Get requests to download mp3 or wav files
import requests

# Used to replace file operations with in memory operations (with ByteIO)
import io

# In memory copy of objects
from copy import copy

# Imports related to the use of S3
import logging
import boto3
from botocore.exceptions import ClientError





class AudioProcessing():
    def __init__(self, url=None, bytes_object=None):
        """
        In memory simple audio operation on wav files. Supports mp3 to wav conversion
        """
        if(url):
            # create file from url
            r = requests.get(url)
            bytes_object = r.content
        
        self.read(bytes_object)
        return

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

    def deepen(self, factor=0.85):
        self.freq = int(self.freq * factor)

    def pitch(self, factor=0.9):
        self.freq = int(self.freq / factor)
    
    def hide_voice (self):
        self.set_volume(1.3)
        #self.custom_filter(1.3)
        self.add_echo(delay=0.02)
        self.deepen(factor=0.8)
        output = io.BytesIO()
        return self.write(output)
    
    def to_bytes(self):
        """
        Returns io.BytesIO stream of the edited mp3
        """
        output = io.BytesIO()
        return self.write(output)

    def read(self, f, normalized=False):
        """MP3 to numpy array"""
        a = pydub.AudioSegment.from_mp3(io.BytesIO(f))
        y = np.array(a.get_array_of_samples())
        if a.channels == 2:
            y = y.reshape((-1, 2))
        if normalized:
            self.audio_data =  np.float32(y) / 2**15
            self.freq = a.frame_rate
            return a.frame_rate, np.float32(y) / 2**15
        else:
            self.audio_data = y
            self.freq = a.frame_rate
            return a.frame_rate, y

    def write(self, f, normalized=False):
        """numpy array to MP3"""
        sr = self.freq
        x = self.audio_data
        channels = 2 if (x.ndim == 2 and x.shape[1] == 2) else 1
        if normalized:  # normalized array - each item should be a float in [-1, 1)
            y = np.int16(x * 2 ** 15)
        else:
            y = np.int16(x)
        song = pydub.AudioSegment(y.tobytes(), frame_rate=sr, sample_width=2, channels=channels)
        song.export(f, format="mp3", bitrate="320k")
        return f


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
        return response
    except ClientError as e:
        print("S3 error occured "+ e)
        return None
    


if __name__ == '__main__':
    
    # print("URL from of mp3 file: ", end="")
    # YOUR_URL = str(input())
    
    YOUR_URL = debug_url
    x = AudioProcessing(bytes_object="who-are-you.mp3")
    # x.set_audio_speed(1.1)
    
    # Deepened voice :
    x.deepen()
    
    # Pitched voice :
    # x.pitch()
    
    
    result = x.to_bytes()
    # upload_file_to_S3(result, BUCKET, "voice_changed.mp3")
    
    with open("slim.mp3", "wb") as f:
        f.write(result.getbuffer())

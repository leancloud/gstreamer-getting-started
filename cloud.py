# coding: utf-8

from datetime import datetime
from datetime import timedelta

from leancloud import Object
from leancloud import ACL
from leancloud import Engine
from leancloud import LeanEngineError
import azure.cognitiveservices.speech as speechsdk
from app import app

 
engine = Engine(app)
class BinaryFileReaderCallback(speechsdk.audio.PullAudioInputStreamCallback):
    def __init__(self, filename: str):
        super().__init__()
        self._file_h = open(filename, "rb")

    def read(self, buffer: memoryview) -> int:
        print('trying to read {} frames'.format(buffer.nbytes))
        try:
            size = buffer.nbytes
            frames = self._file_h.read(size)

            buffer[:len(frames)] = frames
            print('read {} frames'.format(len(frames)))

            return len(frames)
        except Exception as ex:
            print('Exception in `read`: {}'.format(ex))
            raise

    def close(self) -> None:
        print('closing file')
        try:
            self._file_h.close()
        except Exception as ex:
            print('Exception in `close`: {}'.format(ex))
            raise

def compressed_stream_helper(compressed_format,
        mp3_file_path):
    callback = BinaryFileReaderCallback(mp3_file_path)
    stream = speechsdk.audio.PullAudioInputStream(stream_format=compressed_format, pull_stream_callback=callback)

    speech_config =speechsdk.SpeechConfig(subscription="d3d95defb0e44170bce6c2019bc877dc", region="eastasia")
    audio_config = speechsdk.audio.AudioConfig(stream=stream)

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)

    speech_recognizer.stop_continuous_recognition()
    # </SpeechContinuousRecognitionWithFile>

    def pull_audio_input_stream_compressed_mp3(mp3_file_path: str):
        # Create a compressed format
        compressed_format = speechsdk.audio.AudioStreamFormat(compressed_stream_format=speechsdk.AudioStreamContainerFormat.MP3)
        compressed_stream_helper(compressed_format, mp3_file_path)


# @engine.before_save('Todo')
# def before_todo_save(todo):
#     content = todo.get('content')
#     if not content:
#         raise LeanEngineError('内容不能为空')
#     if len(content) >= 240:
#         todo.set('content', content[:240] + ' ...')
#     author = todo.get('author')
#     if author:
#         acl = ACL()
#         acl.set_public_read_access(True)
#         acl.set_read_access(author.id, True)
#         acl.set_write_access(author.id, True)
#         todo.set_acl(acl)


# @engine.define
# def empty_trash():
#     deleted_todos = Object.extend('Todo').query.equal_to('status', -1).less_than('updatedAt', datetime.today() - timedelta(30)).find()
#     if not deleted_todos:
#         print('过去 30 天内没有被删除的 todo')
#     else:
#         print('正在清理{0}条 todo……'.format(len(deleted_todos)))
#         for todo in deleted_todos:
#             todo.destroy()
#         print('清理完成。')




@engine.define
def azureNewInterface(mp3Url,standardText, **params):
   compressed_stream_helper(speechsdk.audio.AudioStreamFormat(), mp3Url)


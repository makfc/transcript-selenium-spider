import glob, os
import hashlib
import io

import logging
logger = logging.getLogger(__name__)


def md5sum(src):
    md5 = hashlib.md5()
    with io.open(src, mode="rb") as fd:
        content = fd.read()
        md5.update(content)
    return md5.hexdigest()


def check_for_files(file_path):
    for file_path_object in glob.glob(file_path):
        if os.path.isfile(file_path_object):
            return True


def remove_all_new_transcript():
    for file in glob.glob("*.pdf"):
        if os.path.isfile(file):
            os.remove(file)


# True when two md5 are different
def is_different_transcript(old_transcript_md5):
    new_transcript_md5 = None
    files = glob.glob("*.pdf")
    if files:
        file = files[0]
        new_transcript_md5 = md5sum(file)
        logger.info('New transcript fileName: %s', file)
        logger.info('Hash: %s', new_transcript_md5)

        # if new_transcript_md5 is None or two md5 are same
        if not new_transcript_md5 or new_transcript_md5 == old_transcript_md5:
            remove_all_new_transcript()
            return False
        else:
            logger.info('old_transcript_md5: %s', old_transcript_md5)
            logger.info('new_transcript_md5: %s', new_transcript_md5)
            return True
    else:
        logger.error('Transcript download failed')
    return False


def get_old_transcript_md5():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + '\old_transcript')
    transcript_md5 = None
    files = glob.glob("*.pdf")
    if files:
        file = files[0]
        transcript_md5 = md5sum(file)
        logger.info('Old transcript fileName: %s', file)
        logger.info('Hash: %s', transcript_md5)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    return transcript_md5

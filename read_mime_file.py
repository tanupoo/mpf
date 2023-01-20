import sys
import email

def read_mime_file(mime_file: str) -> email.message.Message:
    if mime_file is None:
        msg = email.message_from_file(sys.stdin)
    else:
        with open(mime_file, "r") as fd:
            msg = email.message_from_file(fd)
    return msg



import sys
from email.message import Message as emailMessage
from email.header import decode_header, Header
from email import message_from_binary_file
from dateutil.parser import parse as dt_parse
from email import charset as _charset
from typing import Union

def decode_header_more(
        msg: Union[str, Header],
        ) -> str:
    if msg is None:
        return None
    elif isinstance(msg, str):
        """
        either a string or an encoded string such as =?charset?encoding?encoded-text?=
        """
        sbjs = []
        for m in decode_header(msg):
            if m[1] is None:
                if isinstance(m[0], str):
                    sbjs.append(m[0])
                elif isinstance(m[0], bytes):
                    sbjs.append(m[0].decode())
                else:
                    raise ValueError(f"unknown type {m[0]}")
            else:
                sbjs.append(m[0].decode(m[1]))
        ret = "".join(sbjs)
    elif isinstance(msg, Header):
        m2 = []
        for string, charset in msg._chunks:
            if charset == _charset.UNKNOWN8BIT:
                m2.append(string.encode('ascii', 'surrogateescape'))
            else:
                m2.append(string)
        msg = b"".join(m2)
        for c in ["iso-2022-jp", "utf-8", "eucjp", "sjis"]:
            try:
                ret = msg.decode(c)
            except UnicodeDecodeError:
                continue
        else:
            return None
    else:
        raise NotImplemented
    return ret.replace("\n","")

def decode_mime(
        msg: emailMessage,
        decode_id: int=None,
        out_file: str=None,
        verbose: bool=False,
        ) -> None:
    """
    decode_id:
        None means to show the list.
        0 to decode the header
    """
    #
    if decode_id is None:
        def print_hdr(m, hdr_key):
            hdr_value = m.get(hdr_key)
            if hdr_value is not None:
                print(hdr_key, hdr_value)
        #
        for cid,p in enumerate(msg.walk()):
            ct = f"{p.get_content_maintype()}/{p.get_content_subtype()}"
            if cid == 0:
                if verbose:
                    for k,v in p.items():
                        print(f"{k}: {v}")
                else:
                    print(f"\n# {cid}")
                    print(f"Date: {p.get('Date')}")
                    print(f"From: {p.get('From')}")
                    print(f"To: {p.get('To')}")
                    print(f"Subject: {p.get('Subject')}")
            else:
                #print("{}# {}".format("\n" if cid != 1 else "", cid))
                print(f"\n# {cid}")
                if verbose:
                    for k,v in p.items():
                        print(f"{k}: {v}")
                else:
                    print_hdr(p, "Content-Type")
                    print_hdr(p, "Content-Transfer-Encoding")
                body = p.get_payload(decode=True)
                if body is not None:
                    print("size:", len(body))
                else:
                    print("size:", 0)
    else:
        for cid,p in enumerate(msg.walk()):
            ct = f"{p.get_content_maintype()}/{p.get_content_subtype()}"
            # Content-Disposition: attachment; filename="SIG-SWO-056-16.pdf"
            if decode_id == cid:
                body = p.get_payload(decode=True)
                if body is not None:
                    if out_file:
                        with open(out_file, "wb") as fd:
                            fd.write(body)
                    elif ct in [ "text/plain", "text/html" ]:
                        charset = p.get_charsets()[0]
                        print(body.decode(charset))
                    else:
                        print(f"ERROR: the option -o is required for {ct}")
                break

def read_mail_file(mime_file: str) -> emailMessage:
    if mime_file is None:
        msg = message_from_binary_file(sys.stdin)
    else:
        with open(mime_file, "rb") as fd:
            msg = message_from_binary_file(fd)
    return msg

def decode_mime_file(
        mime_file: str,
        decode_id: int=None,
        out_file: str=None,
        verbose: bool=False,
        ) -> None:
    msg = read_mail_file(mime_file)
    decode_mime(msg, decode_id, out_file, verbose)

def get_mail_info(
        path: str,
        ) -> dict:
    """
    convertint text into readable text
    """
    info = {}
    info.update({"Path": path})
    em = read_mail_file(path)
    dt = em.get("Date")
    if dt:
        info.update({"Date": dt_parse(dt, fuzzy_with_tokens=True)[0]})
    else:
        info.update({"Date": None})
    info.update({"Subject": decode_header_more(em.get("Subject"))})
    info.update({"From": decode_header_more(em.get("From"))})
    return info


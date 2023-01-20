
from email.message import Message as emailMessage
from email.header import decode_header
from read_mime_file import read_mime_file

def decode_subject(
        msg: str,
        ) -> str:
    # =?charset?encoding?encoded-text?=
    # XXX need to know the right way.
    sbjs = []
    for m in decode_header(msg):
        if m[1] is None:
            if isinstance(m[0], str):
                sbjs.append(m[0])
            elif isinstance(m[0], bytes):
                sbjs.append(m[0].decode())
            else:
                #raise ValueError(f"unknown type {m[0]}")
                print(m[1])
        elif m[1] == "utf-8":
            sbjs.append(m[0].decode())
        else:
            #raise ValueError(f"unknown charset {m[1]}")
            print(m[1])
    return "".join(sbjs)

def decode_mime(
        msg: emailMessage,
        decode_id: int=None,
        out_file: str=None,
        ) -> None:
    #
    for cid,p in enumerate(msg.walk()):
        ct = f"{p.get_content_maintype()}/{p.get_content_subtype()}"
        # Content-Disposition: attachment; filename="SIG-SWO-056-16.pdf"
        if decode_id is None:
            if cid == 0:
                print(f"# Date: {p.get('Date')}")
                print(f"From: {p.get('From')}")
                print(f"To: {p.get('To')}")
                print(f"Subject: {p.get('Subject')}")
            else:
                #print("{}# {}".format("\n" if cid != 1 else "", cid))
                print(f"\n# {cid}")
                for k,v in p.items():
                    print(f"{k}: {v}")
                #print("content-type", ct)
                #cte = p.get("Content-Transfer-Encoding")
                #if cte is not None:
                #    print("encoding:", cte)
                body = p.get_payload(decode=True)
                if body is not None:
                    print("size:", len(body))
                else:
                    print("size:", 0)
        elif decode_id == cid:
            if cid == 0:
                for k,v in p.items():
                    print(f"{k}: {v}")
            else:
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

def decode_mime_file(
        mime_file: str,
        decode_id: int=None,
        out_file: str=None,
        ) -> None:
    msg = read_mime_file(mime_file)
    decode_mime(msg, decode_id, out_file)

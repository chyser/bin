#!/usr/bin/env python
"""
usage: mailfiles <params> [options] <file_0> [<file_1> [...]]

    params:
        -t : --to         | destination address(es)
        -f : --frm        | senders address

    options:
        -s : --subject     | subject for mail message (default: empty string)
        -n : --nonmime_msg | message for non-mime aware clients (default: subject)

        -m : --mailserver  | smtp mailserver (default: localhost)
        -t : --transport   | normal or SSL/TLS (default: normal)
        -p : --port        | SMTP port (default: 25:normal, 465:TLS)

        -d | --dump        | dump message string to stdout

"""

import pylib.osscripts as oss
import pylib.emaillib as eml
import pylib.net.util as nu

import email

import smtplib
import mimetypes

from email import encoders
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

#-------------------------------------------------------------------------------
def usage(rc, errmsg=""):
#-------------------------------------------------------------------------------
    """ provides doc string as usage information
    """
    print >> oss.stderr, __doc__
    if errmsg:
        print >> oss.stderr, """

Error:
""" + str(errmsg)
    oss.exit(rc)


#-------------------------------------------------------------------------------
def MimifyFiles(fileName_List, msg = None):
#-------------------------------------------------------------------------------
    """ turn a file or list of files 'fileName_List' into a multipart mime msg.
    """
    if msg is None:
        msg = MIMEMultipart()

    if isinstance(fileName_List, (str, unicode)):
        fileName_List = [fileName_List]

    for f in fileName_List:
        ctype, encoding = mimetypes.guess_type(f)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split('/', 1)

        if maintype == 'text':
            fp = file(f)
            imsg = MIMEText(fp.read(), _subtype=subtype)
            fp.close()

        elif maintype == 'image':
            fp = file(f, 'rb')
            imsg = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()

        elif maintype == 'audio':
            fp = file(f, 'rb')
            imsg = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()

        else:
            fp = file(f, 'rb')
            imsg = MIMEBase(maintype, subtype)
            imsg.set_payload(fp.read())
            fp.close()

            # Encode the payload using Base64
            encoders.encode_base64(imsg)

        # Set the filename parameter
        imsg.add_header('Content-Disposition', 'attachment', filename=f)

        msg.attach(imsg)
    return msg

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(argv[1:], [('d', 'dump')], [('t', 'to'), ('f', 'frm'), ('s', 'subject'), ('m', 'mailserver')], usage)

    if not args:
        usage(1, "Must supply one or more files")

    if not opts.to or not opts.frm:
        usage(2, "Must specify dource and destimatiom addresses")

    if opts.mailserver is None:
        opts.mailserver = "localhost"

    if isinstance(opts.to, (str, unicode)):
        opts.to = [opts.to]

    msg = MIMEMultipart()
    msg['From'] = opts.frm
    msg['To'] = ', '.join(opts.to)

    if opts.subject is not None:
        msg['Subject'] = opts.subject
        msg.preamble = opts.subject

    MimifyFiles(args, msg)

    if opts.dump:
        print msg.as_string()
        oss.exit(0)

    # Send the email. Use kirby if available
    if nu.ping('kirby.fc.hp.com'):
        sc = eml.SMTPClient("kirby.fc.hp.com")
    else:
        sc = eml.SMTPClient("mail.hp.com", transport="TLS", debug=True, login = ("chris_hyser@hp.com", "Ifc{2x[mh-Nt5"))

    sc.sendMsg(msg)
    sc.close()

    #s = smtplib.SMTP()
    #s.connect()
    #s.sendmail(opts.frm, opts.to, msg.as_string())
    #s.close()

    oss.exit(0)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(oss.argv)

import urllib2
import hashlib
from boto.s3.connection import S3Connection
from boto.s3.key import Key

def generate_hash(url):
    return hashlib.md5(url).hexdigest()


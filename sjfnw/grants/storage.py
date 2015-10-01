import logging

from django.core.files.storage import Storage
from django.core.files.uploadedfile import UploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers
from django.utils.encoding import force_unicode

from google.appengine.api.images import get_serving_url, NotImageError
from google.appengine.ext.blobstore import BlobInfo, BlobKey, delete, BlobReader

from sjfnw.grants.utils import get_blobkey_from_body

logger = logging.getLogger('sjfnw')

# MODIFIED VERSION OF DJANGOAPPENGINES STORAGE FILE. SEE LICENSE AT BOTTOM

""" Uploading files
  Assume view has set up a form that posts to a blobstore url, so we are getting
  the modified form data with blobinfo in it.

  1. BlobstoreFileUploadHandler.new_file
    a. Extracts blobkey using get_blobkey_from_body
  2. BlobstoreFileUploadHandler.file_complete
  3. BlobstoreUploadedFile.__init__
  4. BlobstoreStorage._save
    a. data is blobinfo, key is stored

  Serving files (via docs viewer or direct)
    Using grants/utils.py
"""

class BlobstoreFileUploadHandler(FileUploadHandler):
  """ File upload handler for the Google App Engine Blobstore. """

  def new_file(self, *args, **kwargs):
    """field_name, file_name, content_type, content_length, charset=None"""

    logger.debug('BlobstoreFileUploadHandler.new_file')
    super(BlobstoreFileUploadHandler, self).new_file(*args, **kwargs)

    blobkey = get_blobkey_from_body(self.request.body)
    self.active = blobkey is not None
    if self.active:
      self.blobkey = BlobKey(blobkey)
      raise StopFutureHandlers()

  def receive_data_chunk(self, raw_data, start):
    """ Add the data to the StringIO file.  """
    if not self.active:
      return raw_data

  def file_complete(self, file_size):
    """ Return a file object if we're activated.  """
    logger.info('BlobstoreFileUploadHandler.file_complete')
    if not self.active:
      logger.info('not active')
      return
    return BlobstoreUploadedFile(
      blobinfo=BlobInfo(self.blobkey),
      charset=self.charset)


class BlobstoreStorage(Storage):
  """ Google App Engine Blobstore storage backend """

  def _open(self, name, mode='rb'):
    raise NotImplementedError()

  def _save(self, name, content):
    logger.info('storage _save on %s', name)
    name = name.replace('\\', '/')

    if hasattr(content, 'file') and hasattr(content.file, 'blobstore_info'):
      data = content.file.blobstore_info
    elif hasattr(content, 'blobstore_info'):
      data = content.blobstore_info
    else:
      raise ValueError('BlobstoreStorage only supports content with blobinfo')

    if isinstance(data, (BlobInfo, BlobKey)):
      if isinstance(data, BlobInfo):
        data = data.key()

      name = name.lstrip('/') # get just the file name
      if len(name) > 65: # shorten name so extension fits in FileField
        name = name.split('.')[0][:60].rstrip() + u'.' + name.split('.')[1]
        logger.info('Returning shortened name: %s', name)

      return '%s/%s' % (data, name)

    else:
      raise ValueError('BlobstoreStorage only supports BlobInfo values. Data '
                       'cannot be uploaded directly; you have to use the file'
                       'upload handler.')

  def delete(self, name):
    delete(self._get_key(name))

  def exists(self, name):
    return self._get_blobinfo(name) is not None

  def size(self, name):
    return self._get_blobinfo(name).size

  def url(self, name):
    try:
      return get_serving_url(self._get_blobinfo(name))
    except NotImageError:
      return None

  def accessed_time(self, name):
    raise NotImplementedError()

  def created_time(self, name):
    return self._get_blobinfo(name).creation

  def get_valid_name(self, name):
    return force_unicode(name).strip().replace('\\', '/')

  def get_available_name(self, name):
    return name.replace('\\', '/')

  def _get_key(self, name):
    return BlobKey(name.split('/', 1)[0])

  def _get_blobinfo(self, name):
    return BlobInfo.get(self._get_key(name))


class BlobstoreUploadedFile(UploadedFile):
  """ A file uploaded into memory (i.e. stream-to-memory)
      See django's InMemoryUploadedFile for a non-blobstore example  """

  def __init__(self, blobinfo, charset):
    logger.info('BlobstoreUploadedFile.__init__ %s', blobinfo.content_type)
    super(BlobstoreUploadedFile, self).__init__(
      BlobReader(blobinfo.key()), # read only file-like interface to blob
      blobinfo.filename, blobinfo.content_type, blobinfo.size, charset)
    self.blobstore_info = blobinfo

  def chunks(self, chunk_size=1024 * 128):
    self.file.seek(0)
    while True:
      content = self.read(chunk_size)
      if not content:
        break
      yield content

  def multiple_chunks(self, chunk_size=1024 * 128):
    return True

#Djangoappengine license:

#Copyright (c) Waldemar Kornewald, Thomas Wanschik, and all contributors.
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification,
#are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of All Buttons Pressed nor
#       the names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS' AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import threading

'''
Reference link: https://www.lifewire.com/file-extensions-and-mime-types-3469109

json / html / htm / doc / docx / ppt / pptx / xls / xlsx / js / pdf / txt
'''

content_file_mapping = {
    '*': {'application': 'Binary file', 'mine': 'application/octet-stream'},
    # Others
    'json': {'application': 'json document', 'mine': 'application/json'},
    'docx': {'application': 'docx document', 'mine': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
    'pptx': {'application': 'pptx document', 'mine': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'},
    'xlsx': {'application': 'xlsx document', 'mine': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
    'pdf': {'application': 'pdf document', 'mine': 'application/pdf'},
    # MIME Types: Applications
    'evy': {'application': 'Corel Envoy', 'mine': 'application/envoy'},
    'doc': {'application': 'Word document', 'mine': 'application/msword'},
    'fif': {'application': 'fractal image file', 'mine': 'application/fractals'},
    'spl': {'application': 'Windows print spool file', 'mine': 'application/futuresplash'},
    'hta': {'application': 'HTML application', 'mine': 'application/hta'},
    'acx': {'application': 'Atari ST Program', 'mine': 'application/internet-property-stream'},
    'hqx': {'application': 'BinHex encoded file', 'mine': 'application/mac-binhex40'},
    'dot': {'application': 'Word document template', 'mine': 'application/msword'},
    'bin': {'application': 'binary disk image', 'mine': 'application/octet-stream'},
    'class': {'application': 'Java class file', 'mine': 'application/octet-stream'},
    'dms': {'application': 'Disk Masher image', 'mine': 'application/octet-stream'},
    'exe': {'application': 'executable file', 'mine': 'application/octet-stream'},
    'lha': {'application': 'LHARC compressed archive', 'mine': 'application/octet-stream'},
    'lzh': {'application': 'LZH compressed file', 'mine': 'application/octet-stream'},
    'oda': {'application': 'CALS raster image', 'mine': 'application/oda'},
    'axs': {'application': 'ActiveX script', 'mine': 'application/olescript'},
    'prf': {'application': 'Outlook profile file', 'mine': 'application/pics-rules'},
    'p10': {'application': 'certificate request file', 'mine': 'application/pkcs10'},
    'crl': {'application': 'certificate revocation list file', 'mine': 'application/pkix-crl'},
    'ai': {'application': 'Adobe Illustrator file', 'mine': 'application/postscript'},
    'eps': {'application': 'postscript file', 'mine': 'application/postscript'},
    'ps': {'application': 'postscript file', 'mine': 'application/postscript'},
    'rtf': {'application': 'rich text format file', 'mine': 'application/rtf'},
    'setpay': {'application': 'set payment initiation', 'mine': 'application/set-payment-initiation'},
    'setreg': {'application': 'set registration initiation', 'mine': 'application/set-registration-initiation'},
    'xla': {'application': 'Excel Add-in file', 'mine': 'application/vnd.ms-excel'},
    'xlc': {'application': 'Excel chart', 'mine': 'application/vnd.ms-excel'},
    'xlm': {'application': 'Excel macro', 'mine': 'application/vnd.ms-excel'},
    'xls': {'application': 'Excel spreadsheet', 'mine': 'application/vnd.ms-excel'},
    'xlt': {'application': 'Excel template', 'mine': 'application/vnd.ms-excel'},
    'xlw': {'application': 'Excel worspace', 'mine': 'application/vnd.ms-excel'},
    'msg': {'application': 'Outlook mail message', 'mine': 'application/vnd.ms-outlook'},
    'sst': {'application': 'serialized certificate store file', 'mine': 'application/vnd.ms-pkicertstore'},
    'cat': {'application': 'Windows catalog file', 'mine': 'application/vnd.ms-pkiseccat'},
    'stl': {'application': 'stereolithography file', 'mine': 'application/vnd.ms-pkistl'},
    'pot': {'application': 'PowerPoint template', 'mine': 'application/vnd.ms-powerpoint'},
    'pps': {'application': 'PowerPoint slide show', 'mine': 'application/vnd.ms-powerpoint'},
    'ppt': {'application': 'PowerPoint presentation', 'mine': 'application/vnd.ms-powerpoint'},
    'mpp': {'application': 'Microsoft Project file', 'mine': 'application/vnd.ms-project'},
    'wcm': {'application': 'WordPerfect macro', 'mine': 'application/vnd.ms-works'},
    'wdb': {'application': 'Microsoft Works database', 'mine': 'application/vnd.ms-works'},
    'wks': {'application': 'Microsoft Works spreadsheet', 'mine': 'application/vnd.ms-works'},
    'wps': {'application': 'Microsoft Works word processsor document', 'mine': 'application/vnd.ms-works'},
    'hlp': {'application': 'Windows help file', 'mine': 'application/winhlp'},
    'bcpio': {'application': 'binary CPIO archive', 'mine': 'application/x-bcpio'},
    'cdf': {'application': 'computable document format file', 'mine': 'application/x-cdf'},
    'z': {'application': 'Unix compressed file', 'mine': 'application/x-compress'},
    'tgz': {'application': 'gzipped tar file', 'mine': 'application/x-compressed'},
    'cpio': {'application': 'Unix CPIO archive', 'mine': 'application/x-cpio'},
    'csh': {'application': 'Photoshop custom shapes file', 'mine': 'application/x-csh'},
    'dcr': {'application': 'Kodak RAW image file', 'mine': 'application/x-director'},
    'dir': {'application': 'Adobe Director movie', 'mine': 'application/x-director'},
    'dxr': {'application': 'Macromedia Director movie', 'mine': 'application/x-director'},
    'dvi': {'application': 'device independent format file', 'mine': 'application/x-dvi'},
    'gtar': {'application': 'Gnu tar archive', 'mine': 'application/x-gtar'},
    'gz': {'application': 'Gnu zipped archive', 'mine': 'application/x-gzip'},
    'hdf': {'application': 'hierarchical data format file', 'mine': 'application/x-hdf'},
    'ins': {'application': 'internet settings file', 'mine': 'application/x-internet-signup'},
    'isp': {'application': 'IIS internet service provider settings', 'mine': 'application/x-internet-signup'},
    'iii': {'application': 'ARC+ architectural file', 'mine': 'application/x-iphone'},
    'js': {'application': 'JavaScript file', 'mine': 'application/x-javascript'},
    'latex': {'application': 'LaTex document', 'mine': 'application/x-latex'},
    'mdb': {'application': 'Microsoft Access database', 'mine': 'application/x-msaccess'},
    'crd': {'application': 'Windows CardSpace file', 'mine': 'application/x-mscardfile'},
    'clp': {'application': 'CrazyTalk clip file', 'mine': 'application/x-msclip'},
    'dll': {'application': 'dynamic link library', 'mine': 'application/x-msdownload'},
    'm13': {'application': 'Microsoft media viewer file', 'mine': 'application/x-msmediaview'},
    'm14': {'application': 'Steuer2001 file', 'mine': 'application/x-msmediaview'},
    'mvb': {'application': 'multimedia viewer book source file', 'mine': 'application/x-msmediaview'},
    'wmf': {'application': 'Windows meta file', 'mine': 'application/x-msmetafile'},
    'mny': {'application': 'Microsoft Money file', 'mine': 'application/x-msmoney'},
    'pub': {'application': 'Microsoft Publisher file', 'mine': 'application/x-mspublisher'},
    'scd': {'application': 'Turbo Tax tax schedule list', 'mine': 'application/x-msschedule'},
    'trm': {'application': 'FTR media file', 'mine': 'application/x-msterminal'},
    'wri': {'application': 'Microsoft Write file', 'mine': 'application/x-mswrite'},
    'nc': {'application': 'Mastercam numerical control file', 'mine': 'application/x-netcdf'},
    'pma': {'application': 'MSX computers archive format', 'mine': 'application/x-perfmon'},
    'pmc': {'application': 'performance monitor counter file', 'mine': 'application/x-perfmon'},
    'pml': {'application': 'process monitor log file', 'mine': 'application/x-perfmon'},
    'pmr': {'application': 'Avid persistant media record file', 'mine': 'application/x-perfmon'},
    'pmw': {'application': 'Pegasus Mail draft stored message', 'mine': 'application/x-perfmon'},
    'p12': {'application': 'personal information exchange file', 'mine': 'application/x-pkcs12'},
    'pfx': {'application': 'PKCS #12 certificate file', 'mine': 'application/x-pkcs12'},
    'p7b': {'application': 'PKCS #7 certificate file', 'mine': 'application/x-pkcs7-certificates'},
    'spc': {'application': 'software publisher certificate file', 'mine': 'application/x-pkcs7-certificates'},
    'p7r': {'application': 'certificate request response file', 'mine': 'application/x-pkcs7-certreqresp'},
    'p7c': {'application': 'PKCS #7 certificate file', 'mine': 'application/x-pkcs7-mime'},
    'p7m': {'application': 'digitally encrypted message', 'mine': 'application/x-pkcs7-mime'},
    'p7s': {'application': 'digitally signed email message', 'mine': 'application/x-pkcs7-signature'},
    'sh': {'application': 'Bash shell script', 'mine': 'application/x-sh'},
    'shar': {'application': 'Unix shar archive', 'mine': 'application/x-shar'},
    'swf': {'application': 'Flash file', 'mine': 'application/x-shockwave-flash'},
    'sit': {'application': 'Stuffit archive file', 'mine': 'application/x-stuffit'},
    'sv4cpio': {'application': 'system 5 release 4 CPIO file', 'mine': 'application/x-sv4cpio'},
    'sv4crc': {'application': 'system 5 release 4 CPIO checksum data', 'mine': 'application/x-sv4crc'},
    'tar': {'application': 'consolidated Unix file archive', 'mine': 'application/x-tar'},
    'tcl': {'application': 'Tcl script', 'mine': 'application/x-tcl'},
    'tex': {'application': 'LaTeX source document', 'mine': 'application/x-tex'},
    'texi': {'application': 'LaTeX info document', 'mine': 'application/x-texinfo'},
    'texinfo': {'application': 'LaTeX info document', 'mine': 'application/x-texinfo'},
    'roff': {'application': 'unformatted manual page', 'mine': 'application/x-troff'},
    't': {'application': 'Turing source code file', 'mine': 'application/x-troff'},
    'tr': {'application': 'TomeRaider 2 ebook file', 'mine': 'application/x-troff'},
    'man': {'application': 'Unix manual', 'mine': 'application/x-troff-man'},
    'me': {'application': 'readme text file', 'mine': 'application/x-troff-me'},
    'ms': {'application': '3ds Max script file', 'mine': 'application/x-troff-ms'},
    'ustar': {'application': 'uniform standard tape archive format file', 'mine': 'application/x-ustar'},
    'src': {'application': 'source code', 'mine': 'application/x-wais-source'},
    'cer': {'application': 'internet security certificate', 'mine': 'application/x-x509-ca-cert'},
    'crt': {'application': 'security certificate', 'mine': 'application/x-x509-ca-cert'},
    'der': {'application': 'DER certificate file', 'mine': 'application/x-x509-ca-cert'},
    'pko': {'application': 'public key security object', 'mine': 'application/ynd.ms-pkipko'},
    'zip': {'application': 'zipped file', 'mine': 'application/zip'},
    # MIME Types: Sound Files
    'au': {'application': 'audio file', 'mine': 'audio/basic'},
    'snd': {'application': 'sound file', 'mine': 'audio/basic'},
    'mid': {'application': 'midi file', 'mine': 'audio/mid'},
    'rmi': {'application': 'media processing server studio', 'mine': 'audio/mid'},
    'mp3': {'application': 'MP3 file', 'mine': 'audio/mpeg'},
    'aif': {'application': 'audio interchange file format', 'mine': 'audio/x-aiff'},
    'aifc': {'application': 'compressed audio interchange file', 'mine': 'audio/x-aiff'},
    'aiff': {'application': 'audio interchange file format', 'mine': 'audio/x-aiff'},
    'm3u': {'application': 'media playlist file', 'mine': 'audio/x-mpegurl'},
    'ra': {'application': 'Real Audio file', 'mine': 'audio/x-pn-realaudio'},
    'ram': {'application': 'Real Audio metadata file', 'mine': 'audio/x-pn-realaudio'},
    'wav': {'application': 'WAVE audio file', 'mine': 'audio/x-wav'},
    # MIME Types: Image Files
    'bmp': {'application': 'Bitmap', 'mine': 'image/bmp'},
    'cod': {'application': 'compiled source code', 'mine': 'image/cis-cod'},
    'gif': {'application': 'graphic interchange format', 'mine': 'image/gif'},
    'ief': {'application': 'image file', 'mine': 'image/ief'},
    'jpe': {'application': 'JPEG image', 'mine': 'image/jpeg'},
    'jpeg': {'application': 'JPEG image', 'mine': 'image/jpeg'},
    'jpg': {'application': 'JPEG image', 'mine': 'image/jpeg'},
    'jfif': {'application': 'JPEG file interchange format', 'mine': 'image/pipeg'},
    'svg': {'application': 'scalable vector graphic', 'mine': 'image/svg+xml'},
    'tif': {'application': 'TIF image', 'mine': 'image/tiff'},
    'tiff': {'application': 'TIF image', 'mine': 'image/tiff'},
    'ras': {'application': 'Sun raster graphic', 'mine': 'image/x-cmu-raster'},
    'cmx': {'application': 'Corel metafile exchange image file', 'mine': 'image/x-cmx'},
    'ico': {'application': 'icon', 'mine': 'image/x-icon'},
    'pnm': {'application': 'portable any map image', 'mine': 'image/x-portable-anymap'},
    'pbm': {'application': 'portable bitmap image', 'mine': 'image/x-portable-bitmap'},
    'pgm': {'application': 'portable graymap image', 'mine': 'image/x-portable-graymap'},
    'ppm': {'application': 'portable pixmap image', 'mine': 'image/x-portable-pixmap'},
    'rgb': {'application': 'RGB bitmap', 'mine': 'image/x-rgb'},
    'xbm': {'application': 'X11 bitmap', 'mine': 'image/x-xbitmap'},
    'xpm': {'application': 'X11 pixmap', 'mine': 'image/x-xpixmap'},
    'xwd': {'application': 'X-Windows dump image', 'mine': 'image/x-xwindowdump'},
    # MIME Types: Virtual World Files
    'flr': {'application': 'Flare decompiled actionscript file', 'mine': 'x-world/x-vrml'},
    'vrml': {'application': 'VRML file', 'mine': 'x-world/x-vrml'},
    'wrl': {'application': 'VRML world', 'mine': 'x-world/x-vrml'},
    'wrz': {'application': 'compressed VRML world', 'mine': 'x-world/x-vrml'},
    'xaf': {'application': '3ds max XML animation file', 'mine': 'x-world/x-vrml'},
    'xof': {'application': 'Reality Lab 3D image file', 'mine': 'x-world/x-vrml'},
    # MIME Types: Video Files
    'mp2': {'application': 'MPEG-2 audio file', 'mine': 'video/mpeg'},
    'mpa': {'application': 'MPEG-2 audio file', 'mine': 'video/mpeg'},
    'mpe': {'application': 'MPEG movie file', 'mine': 'video/mpeg'},
    'mpeg': {'application': 'MPEG movie file', 'mine': 'video/mpeg'},
    'mpg': {'application': 'MPEG movie file', 'mine': 'video/mpeg'},
    'mpv2': {'application': 'MPEG-2 video stream', 'mine': 'video/mpeg'},
    'mp4': {'application': 'MPEG-4', 'mine': 'video/mp4'},
    'mov': {'application': 'Apple QuickTime movie', 'mine': 'video/quicktime'},
    'qt': {'application': 'Apple QuickTime movie', 'mine': 'video/quicktime'},
    'lsf': {'application': 'Logos library system file', 'mine': 'video/x-la-asf'},
    'lsx': {'application': 'streaming media shortcut', 'mine': 'video/x-la-asf'},
    'asf': {'application': 'advanced systems format file', 'mine': 'video/x-ms-asf'},
    'asr': {'application': 'ActionScript remote document', 'mine': 'video/x-ms-asf'},
    'asx': {'application': 'Microsoft ASF redirector file', 'mine': 'video/x-ms-asf'},
    'avi': {'application': 'audio video interleave file', 'mine': 'video/x-msvideo'},
    'movie': {'application': 'Apple QuickTime movie', 'mine': 'video/x-sgi-movie'},
    # MIME Types: Text Files
    'css': {'application': 'Cascading Style Sheet', 'mine': 'text/css'},
    '323': {'application': 'H.323 internet telephony file', 'mine': 'text/h323'},
    'htm': {'application': 'HTML file', 'mine': 'text/html'},
    'html': {'application': 'HTML file', 'mine': 'text/html'},
    'stm': {'application': 'Exchange streaming media file', 'mine': 'text/html'},
    'uls': {'application': 'NetMeeting user location service file', 'mine': 'text/iuls'},
    'bas': {'application': 'BASIC source code file', 'mine': 'text/plain'},
    'c': {'application': 'C/C++ source code file', 'mine': 'text/plain'},
    'h': {'application': 'C/C++/Objective C header file', 'mine': 'text/plain'},
    'txt': {'application': 'text file', 'mine': 'text/plain'},
    'rtx': {'application': 'rich text file', 'mine': 'text/richtext'},
    'sct': {'application': 'Scitext continuous tone file', 'mine': 'text/scriptlet'},
    'tsv': {'application': 'tab separated values file', 'mine': 'text/tab-separated-values'},
    'htt': {'application': 'hypertext template file', 'mine': 'text/webviewhtml'},
    'htc': {'application': 'HTML component file', 'mine': 'text/x-component'},
    'etx': {'application': 'TeX font encoding file', 'mine': 'text/x-setext'},
    'vcf': {'application': 'vCard file', 'mine': 'text/x-vcard'},
    # MIME Types: Mail Message Files
    'mht': {'application': 'MHTML web archive', 'mine': 'message/rfc822'},
    'mhtml': {'application': 'MIME HTML file', 'mine': 'message/rfc822'},
    'nws': {'application': 'Windows Live Mail newsgroup file', 'mine': 'message/rfc822'},
}


def get_content_type_v1(extension):
    current_type = 'application/octet-stream'

    try:
        current_type = content_file_mapping[extension]['mine']
    except Exception as e:
        pass

    return current_type


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


class SwitchContentFileType(metaclass=SingletonType):
    def __init__(self):
        self.content2file_type_mapping = {}
        self.file2content_type_mapping = {}
        # To load all mapping data
        for key, value in content_file_mapping.items():
            # print(key, value['mine'])
            self.file2content_type_mapping[key] = value['mine']
            if value['mine'] in self.content2file_type_mapping:
                self.content2file_type_mapping[value['mine']].append(key)
            else:
                self.content2file_type_mapping[value['mine']] = [key]

    def content2file_type(self, content_type):
        current_type = ['*']
        try:
            current_type = self.content2file_type_mapping[str(content_type).strip().lower()]
        except Exception as e:
            pass
        return current_type

    def file2content_type(self, file_type):
        current_type = 'application/octet-stream'
        try:
            current_type = self.file2content_type_mapping[str(file_type).strip().lower()]
        except Exception as e:
            pass
        return current_type


def content2file_type(content_type):
    switch_content_file_type = SwitchContentFileType()
    return switch_content_file_type.content2file_type(content_type)


def file2content_type(file_type):
    switch_content_file_type = SwitchContentFileType()
    return switch_content_file_type.file2content_type(file_type)


if __name__ == '__main__':
    # print(get_content_type_v1('json'))
    print(content2file_type(content_type='application/octet-streamxxx'))
    print(file2content_type(file_type='json sdsd'))

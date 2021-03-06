import hashlib
import logging
import os
import snmpy.module
import snmpy.parser
import stat


class file_value(snmpy.module.ValueModule):
    kind = {
        stat.S_IFDIR:  'directory',
        stat.S_IFCHR:  'character device',
        stat.S_IFBLK:  'block device',
        stat.S_IFREG:  'regular file',
        stat.S_IFIFO:  'named pipe',
        stat.S_IFLNK:  'symbolic link',
        stat.S_IFSOCK: 'socket',
    }

    def __init__(self, conf):
        if conf.get('use_stat'):
            conf['items'] = [
                {'file_name':  {'type': 'string',    'func': lambda x: self.conf['object']}},
                {'file_type':  {'type': 'string',    'func': lambda x: self.kind[stat.S_IFMT(x)]}},
                {'file_mode':  {'type': 'string',    'func': lambda x: '%04o' % stat.S_IMODE(x)}},
                {'file_atime': {'type': 'integer64', 'func': lambda x: int(x)}},
                {'file_mtime': {'type': 'integer64', 'func': lambda x: int(x)}},
                {'file_ctime': {'type': 'integer64', 'func': lambda x: int(x)}},
                {'file_nlink': {'type': 'integer',   'func': lambda x: x}},
                {'file_size':  {'type': 'integer',   'func': lambda x: x}},
                {'file_ino':   {'type': 'integer',   'func': lambda x: x}},
                {'file_uid':   {'type': 'integer',   'func': lambda x: x}},
                {'file_gid':   {'type': 'integer',   'func': lambda x: x}},
            ] + conf.get('items', [])
        if conf.get('use_hash'):
            conf['items'].append({'file_md5': {'type': 'string'}})


        snmpy.module.ValueModule.__init__(self, conf)

    def md5sum(self):
        md5 = hashlib.md5()
        with open(self.conf['object'], 'rb') as f:
            for part in iter(lambda: f.read(1024 * md5.block_size), b''):
                md5.update(part)

        return md5.hexdigest()

    def update(self):
        info = text = hash = None

        if self.conf.get('use_stat'):
            info = os.lstat(self.conf['object'])
            logging.debug('%s: %s', self.conf['object'], info)
        if self.conf.get('use_text'):
            text = open(self.conf['object']).read()
            logging.debug('%s: read %d bytes', self.conf['object'], len(text))
        if self.conf.get('use_hash'):
            hash = self.md5sum()
            logging.debug('%s: computed md5sum: %s', self.conf['object'], hash)

        for item in self:
            if hasattr(self[item], 'func') and info:
                self[item] = self[item].func(getattr(info, 'st_%s' % item[5:], info.st_mode))
            elif item == 'file_md5':
                self[item] = hash
            elif text:
                self[item] = snmpy.parser.parse_value(text, self[item])

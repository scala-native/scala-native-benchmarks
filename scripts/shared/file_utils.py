import os
import errno
import subprocess as subp


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def touch(path):
    open(path, 'w+').close()

def slurp(path):
    with open(path) as f:
        return f.read().strip()


def where(cmd):
    if os.path.isfile(cmd):
        return cmd
    else:
        paths = os.environ['PATH'].split(os.pathsep)
        for p in paths:
            f = os.path.join(p, cmd)
            if os.path.isfile(f):
                return f
        else:
            return None


def run(cmd):
    print(">>> " + str(cmd))
    return subp.check_output(cmd)


def dict_from_file(settings_file):
    kv = {}
    with open(settings_file) as settings:
        for line in settings.readlines():
            key, raw_value = line.split('=')
            value = raw_value.strip()
            kv[key] = value
    return kv


def dict_to_file(settings_file, kv):
    with open(settings_file, 'w+') as settings:
        for k, v in kv.iteritems():
            settings.write('{}={}'.format(k, v))


sbt = where('sbt')

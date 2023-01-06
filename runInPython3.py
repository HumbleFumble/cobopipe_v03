import os.path

from getConfig import getConfigClass
CC = getConfigClass()

from Log.CoboLoggers import getLogger
logger = getLogger()

def convertFuncToString(_func, *args, **kwargs):
    print(args)
    #_string = 'from ' + str(_func.__module__) + ' import ' + str(_func.__name__)
    _string = ''
    _string = _string + ';' + _func.__name__ + '('
    
    for i, arg in enumerate(args):
        if callable(arg):
            _string = _string + arg.__name__
        elif type(arg) == type(''):
            _string =  _string + '\'' + arg + '\''
        else:
            _string = _string + str(arg)

        if not i+1 == len(args) or len(kwargs) > 0:
            _string = _string + ', '

    for i, key in enumerate(kwargs):
        kwarg = kwargs[key]
        if type(kwarg) == type(''):
            _string = _string + key + '=\'' + kwarg + '\''
        else:
            _string = _string + key + '=' + str(kwarg) + '' 

        if not i+1 == len(kwargs):
            _string = _string + ', '

    _string = _string + ')'
            
    return _string


def getReturn(_func, *args, **kwargs):
    my_return = _func(*args,**kwargs)
    print('>>CUT-START<<' + str(my_return) + '>>CUT-END<<')


def runInPython3(_func, *args, **kwargs):
    from runtimeEnv import getRuntimeEnvFromConfig
    from subprocess import Popen, PIPE
    python_exe = CC.python3
    if not os.path.exists(python_exe):
        python_exe = "python"

    # PUT IN GET RETURN
    
    _string = python_exe + ' -c \"from runInPython3 import getReturn;' + 'from ' + _func.__module__ + ' import ' + _func.__name__ + convertFuncToString(getReturn, _func, *args,**kwargs) + '\"'
    logger.info('\nRUNNING:: ' + _string + '\n')
    

    runEnvironment = getRuntimeEnvFromConfig(config_class=CC, local_user=True)
    proc = Popen(_string, env=runEnvironment, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    logger.info("Finsihed this func: %s" % _func.__name__)
    logger.info('STDOUT:: ' + str(stdout))
    logger.info('STDERR:: ' + str(stderr))
    print('\nSTDOUT:: ' + str(stdout))
    print('\nSTDERR:: ' + str(stderr))

    return str(stdout).split('>>CUT-START<<')[-1].split('>>CUT-END<<')[0]


if __name__ == '__main__':
    from Preview.general import getPreview
    title = 'E01_SQ020_SH030'
    result = runInPython3(getPreview, title, type='anim', create=True, force=True, local=True)
    print('\nRESULT:: ' + result)
    print('\n>> DONE <<')
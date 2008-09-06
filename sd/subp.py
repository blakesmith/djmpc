import sys

# CommandError exception
class CommandError(Exception):
    _cmd = ''
    _inner_msg = ''

    def __init__(self, cmd, inner_msg):
        self._cmd = cmd
        self._inner_msg = inner_msg

    def __str__(self):
        return repr(('An error occurred while executing the following command: \'%s\'.\n\n%s')%(self._cmd,
                                                                                                self._inner_msg))

# Execute cmd
    def _execute_cmd(cmd, return_stdout, throw_exception_on_error):
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdout, stderr = proc.communicate()

            if (proc.returncode != 0):
                if (throw_exception_on_error):
                    raise CommandError(cmd, stderr)

                return False

            if (return_stdout):
                return stdout

            return True
        except CommandError:
            raise
        except:
            if (throw_exception_on_error):
                raise CommandError(cmd, str(sys.exc_info()))

        return False

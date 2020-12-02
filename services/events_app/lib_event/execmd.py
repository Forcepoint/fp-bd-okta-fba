#
# Author:  Dlo Bagari
# created Date: 12-10-2019
import subprocess
from subprocess import Popen
import json


class ExeCmd:
    def __init__(self):
        pass

    def run(self, cmd):
        process = Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, errors = process.communicate()
        if len(output.decode()) == 0:
            return None, errors
        return json.loads(output), errors

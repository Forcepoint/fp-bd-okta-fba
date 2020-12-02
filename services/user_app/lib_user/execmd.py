
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


if __name__ == "__main__":
    ex = ExeCmd()
    output, error = ex.run('curl -X GET "https://rose-iamlab.wbsntest.net:9500/v1/entity/list/monitored" -H "accept: application/json" -k')
    print(output)

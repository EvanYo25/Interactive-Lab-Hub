import os

dir = "A1B2"

cmd = os.popen("sshpass -p 'ch956@cornell.edu' scp -r pi@100.64.0.210:~/myfiles/" + dir + " ./localfiles/")
cmd.read()

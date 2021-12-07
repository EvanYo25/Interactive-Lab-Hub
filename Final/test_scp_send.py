import os

tar_file = "testsending2.txt"
dir = "A1B2"

cmd = os.popen("sshpass -p 'ch956@cornell.edu' scp ./" + tar_file + " pi@100.64.0.210:~/myfiles/" + dir)
cmd.read()

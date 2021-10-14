import os
while(1):
	sentence = input()
	cmd = "espeak -ven+f2 -k5 -s150 --stdout  \'" + sentence + "\' | aplay"
	returned_value = os.system(cmd)



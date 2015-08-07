import subprocess, time, sys

#Example: benchmark.py caQtDM results-caqtdm

manager = sys.argv[1]
filename = sys.argv[2]

f = open(filename, "w")
screens = 0

if manager == 'edm':
	command = ['edm', '-x']

elif manager == 'caQtDM':
	command = ['/afs/slac/g/lcls/epics/R3-14-12-4_1-0/extensions/extensions-R3-14-12_Dev/src/caQtDM/caqtdm-tradestudy/caQtDM_Binaries/caQtDM']

elif manager == 'epicsQt':
	command = ['qegui']

elif manager == 'CSS':
	command = ['../css-x64/sns-css-4.0.0/css']

else:
	print 'Invalid option'
	sys.exit()

while screens < 100:

	screens += 1

	if manager == 'edm':
		command.append(manager.lower() + "/%d.edl" % screens)	
	elif manager == 'CSS':
		command.append(manager.lower() + "/%d.opi" % screens)
	else:
		command.append(manager.lower() + "/%d.ui" % screens)

	proc = subprocess.Popen(command)
	pid = proc.pid

	if manager == 'CSS':
		#Need to find Eclipse pid

		pid_found = False
		tries = 0

		while not pid_found:
			out = subprocess.Popen(['ps', 'v'], stdout=subprocess.PIPE).communicate()[0].split(b'\n')

			for o in out:
				if 'eclipse' in o:
					pid = int(o.split()[0])
					pid_found = True
					break

			tries +=1
			time.sleep(1)

			#If Eclipse was not found after 10 seconds, the process was not started
			if tries == 10:
				print 'Trying to run CSS again'
				proc = subprocess.Popen(command)
				tries = 0


	if manager == 'CSS':
		time.sleep(30)
	else:
		time.sleep(10+(0.25*))

	mem = 0.0
	cpu = 0.0

	for i in range(10):
		print "Measurement #%d" % (i+1)
		out = subprocess.Popen(['ps', 'v', '-p', str(pid)], stdout=subprocess.PIPE).communicate()[0].split(b'\n')
		vsz_index = out[0].split().index(b'RSS')
		mem += float(out[1].split()[vsz_index])

		out = subprocess.Popen(['ps', '-p', str(pid), '-o', '%cpu'], stdout=subprocess.PIPE).communicate()[0].split(b'\n')
		cpu_index = out[0].split().index(b'%CPU')
		cpu += float(out[1].split()[cpu_index])

		time.sleep(1)

	mem = mem/10.0
	cpu = cpu/10.0

	print "screens = %d, memory = %f, cpu = %f" % (screens, mem, cpu)
	f.write("%d - %f - %f\n" % (screens, mem, cpu))

	if manager == 'CSS':
		subprocess.Popen(['kill','-9', str(pid)])

	proc.kill()	

f.close()
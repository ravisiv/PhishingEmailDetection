import sys
import hashlib
import os
import traceback
import mailbox
import bs4
import email
import yaml
import phdcommon as conf
import random

def savemsgtofile(dir_to_write, msg):
    filename = dir_to_write + conf.get_sha1_hash(msg.as_string())
    with open(filename, 'w') as out:
        gen = email.generator.Generator(out)
        gen.flatten(msg)


def get_next_partition(msgdir):
	curdir =  next(os.walk(msgdir))[1]
	if len(curdir) == 0:
		return 30000
	else:
		return int(max(curdir)) + 1

## Main Func


msgdir = conf.get_target("msgdir")
print("msgdir", msgdir)

mboxfile = sys.argv[1]

print("Processing", mboxfile)
mboxtype = ""
if "phishing" in mboxfile.lower():
	mboxtype = "phishing"
elif "spam" in mboxfile.lower():
	mboxtype = "spam"
elif "promotions" in mboxfile.lower():
	mboxtype = "promotions"

mbox_obj = mailbox.mbox(mboxfile)

size=500
partition = get_next_partition(msgdir)
status = True
while status:
	target_dir = f"{msgdir}/{partition}/"
	if not os.path.exists(target_dir):
		status = False
		try:
			os.makedirs(target_dir)
			with open(f"{target_dir}/.msgtype", 'w') as f:
				f.write("msgtype="+mboxtype + "\n")
				f.write("file="+mboxfile + "\n")
				f.close()
		except:
			sleep(random.randint(0, 9))
			partition = get_next_partition(msgdir)
			continue
	else:
		partition = get_next_partition(msgdir)
	
total_processed = 0
for idx, email_obj in enumerate(mbox_obj):
	try:
		count = idx % size
		if count == size -1:
			partition += 1
		
		target_dir = f"{msgdir}/{partition}/"
		if not os.path.exists(target_dir):
			os.makedirs(target_dir)
			with open(f"{target_dir}/.msgtype", 'w') as f:
				f.write("msgtype="+mboxtype + "\n")
				f.write("file="+mboxfile + "\n")
				f.close()
		savemsgtofile(target_dir,email_obj)
		total_processed += 1
	except Exception as e:
		print("Skipped an message due to error", str(e))
		continue
print("Total msg processed", total_processed)
#End Main


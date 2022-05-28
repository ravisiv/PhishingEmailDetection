import sys
import hashlib
import os
import traceback
import mailbox
import bs4
import email
import yaml

def get_sha1_hash(msg):
    BUF_SIZE = 67108864  # lets read stuff in 64kb chunks!
    sha1 = hashlib.sha1()
    sha1.update(msg.as_string().encode('utf-8'))
    return sha1.hexdigest()


def savemsgtofile(dir_to_write, msg):
    filename = dir_to_write + get_sha1_hash(msg)
    print(filename)
    with open(filename, 'w') as out:
        gen = email.generator.Generator(out)
        gen.flatten(msg)

conf_file = "/work/users/rsivaraman/capstone/conf/msgparser.yaml"

def get_target_dir():
	default_dir = "/scratch/users/rsivaraman/masterdata/msgfiles"
	with open(conf_file, "r") as stream:
		try:
			conf_data = yaml.safe_load(stream)
			return conf_data["msgdir"]
		except yaml.YAMLError as exc:
			return default_dir
	return default_dir

def get_next_partition():
	curdir =  next(os.walk(dir_to_write))[1]
	if len(curdir) == 0:
		return 100
	else:
		return int(max(curdir)) + 1

## Main Func
mboxfile = sys.argv[1]
mboxtype = ""
if "phishing" in mboxfile.lower():
	mboxtype = "phishing"
elif "spam" in mboxfile.lower():
	mboxtype = "spam"
elif "promotions" in mboxfile.lower():
	mboxtype = "promotions"

mbox_obj = mailbox.mbox(mboxfile)

size=100

dir_to_write = get_target_dir()
partition = get_next_partition()
status = True
while status:
	target_dir = f"{dir_to_write}/{partition}/"
	if not os.path.exists(target_dir):
		status = False
		try:
			os.makedirs(target_dir)
			with open(f"{target_dir}/.msgtype", 'w') as f:
				f.write("msgtype="+mboxtype + "\n")
				f.write("file="+mboxfile + "\n")
				f.close()
		except:
			sleep(5)
			partition = get_next_partition()
			continue
	else:
		partition = get_next_partition()
	

for idx, email_obj in enumerate(mbox_obj):
	try:
		count = idx % size
		if count == size -1:
			partition += 1
		
		target_dir = f"{dir_to_write}/{partition}/"
		if not os.path.exists(target_dir):
			os.makedirs(target_dir)
			with open(f"{target_dir}/.msgtype", 'w') as f:
				f.write("msgtype="+mboxtype + "\n")
				f.write("file="+mboxfile + "\n")
				f.close()
		savemsgtofile(target_dir,email_obj)
	except Exception as e:
		print(str(e))
		continue

#End Main


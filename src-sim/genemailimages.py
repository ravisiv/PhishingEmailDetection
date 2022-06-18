from pathlib import Path
from html2image import Html2Image
import os
import email


def gen_email_image(msgfile):
    with open(msgfile, encoding="latin1") as f:
        f_realpath = os.path.realpath(f.name)
        x = email.message_from_file(f)
        body = get_body_html(x)

        bname = os.path.basename(msgfile)
        msg_dname = os.path.dirname(msgfile)
        htmlfile="/dev/shm/ravisiv/{bname}.html"
        dname = os.path.dirname(htmlfile)
        Path(dname).mkdir(parents=True, exist_ok=True)
        f = open( htmlfile, "w")
        f.write(body)
        f.close()
        os.remove(htmlfile)
        hti = Html2Image(size=(1280, 800), output_path=msg_dname)
        hti.screenshot( url=outfile,  save_as=f'{bname}.png')
        return True


#Main Method
if sys.argv[1] == None or sys.argv[1] == "":
    print("Argument msg files folder required!")
    exit(0)

data_path = sys.argv[1]

cur_files = next(os.walk(data_path))[2]
for file in cur_files:
    with open(f"{data_path}/{file}") as f:
        f_realpath = os.path.realpath(f.name)
        if not ".msgtype" in f.name:
            try:
                gen_email_image(msg)
                print(".", end=" ")
            except Exception as e:
                print("--------------------------------starting------------")
                print(traceback.format_exc())
                print("--------------------------------ending------------")
                continue

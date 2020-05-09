"""
Scripting up gimp in Python!
"""
import glob
import subprocess

# see here: https://stackoverflow.com/questions/44430081/how-to-run-python-scripts-using-gimpfu-from-windows-command-line
template = {
    "jpg_to_xcf": """gimp-console -idf --batch-interpreter python-fu-eval -b "import sys;sys.path.insert(0, '/home/chapman/Github/opensandwich/gimp-plugins'); import jpg_to_xcf; jpg_to_xcf.jpg_to_xcf('{}',)" -b "pdb.gimp_quit(1)" """,
    "xcf_to_jpg": """gimp-console -idf --batch-interpreter python-fu-eval -b "import sys;sys.path.insert(0, '/home/chapman/Github/opensandwich/gimp-plugins'); import xcf_to_jpg; xcf_to_jpg.xcf_to_jpg('{}',)" -b "pdb.gimp_quit(1)" """,
}


for f in glob.glob("../夏天只是一天/scans/ch15/*.jpg"):
    print(f)
    shcode = template["jpg_to_xcf"].format(f)
    subprocess.call(shcode, shell=True)

for f in glob.glob("../夏天只是一天/scans/ch14/*.xcf"):
    print(f)
    shcode = template["xcf_to_jpg"].format(f)
    subprocess.call(shcode, shell=True)

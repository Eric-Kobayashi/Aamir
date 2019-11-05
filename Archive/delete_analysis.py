import shutil as sh
import os
import os.path as op

# Path to image folder
pa = r"F:\Dropbox (Cambridge University)\Artemisia\Aamir\Day3-DAPI\Images"

if __name__ in ['__main__', '__builtin__']:
	list_of_dirs = []
	list_of_files = []
	for roots, dirs, files in os.walk(pa):
		for d in dirs:
			if d in ["cell_quant", "comps", "threshold", "qupath_project"]:
				list_of_dirs.append(op.join(roots, d))
		for f in files:
			if f in ['RunMe.groovy']:
				list_of_files.append(op.join(roots, f))
	for f in list_of_files:
		try:
			os.remove(f)
		except:
			pass
	for d in list_of_dirs:
		try:
			sh.rmtree(d)
		except:
			pass
	print('All analysis deleted.')
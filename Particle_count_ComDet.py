import os
import os.path as op
from ij import IJ
from ij import WindowManager as wm
import time

pa = r"E:\Dropbox (Cambridge University)\Artemisia\Aamir\Day3-DAPI\Tau"
ch1a_arr = [3]
ch1s_arr = [40]

def analysis(pa, ch1a, ch1s):
	IJ.run("Close All", "")
	List_of_images = []
	flag = False
	try:
		for roots, dirs, files in os.walk(pa):
			for f in files:
				if f.endswith('.tif') and 'FITC' in f:
					List_of_images.append(op.join(roots, f))
	except:
		List_of_images = wm.getImageTitles()
		flag = True
							
	for tit in List_of_images:
		IJ.run("Clear Results")
		try:
			if flag:
				imp = wm.getImage(tit)
				t = tit
			else:
				imp = IJ.openImage(tit)
				t = op.basename(tit)
		except:
			print('No images detected!')
			continue
#		t = t.replace(" ", "_")
		result_path = op.join(pa, "summary.csv")
		try:
			IJ.redirectErrorMessages()
			IJ.run(imp, "Detect Particles", "ch1a={} ch1s={} add=Nothing".format(ch1a, ch1s))
		except:
			with open(op.join(pa, "summary.csv"), 'w') as s:
				contents = "0\n"
				s.write("{},{},{},{}".format(t.replace(".tif", ""), ch1a, ch1s, contents))
		else:
			IJ.selectWindow("Summary")
			IJ.saveAs("text", result_path)

		with open(op.join(pa, "particle_counts.csv"), 'a') as s:
			with open(result_path, 'r') as rf:
				for lines in rf:
					if 'Channel' not in lines:
						contents = lines.split(',')[-1]
			s.write("{},{},{},{}".format(t.replace(".tif", ""), ch1a, ch1s, contents))
		imp.close()

	os.remove(result_path)
		
if __name__ in ["__main__", "__builtin__"]:
	IJ.run("Input/Output...", "jpeg=85 gif=-1 file=.csv use_file copy_column save_column save_row")
	with open(op.join(pa, "particle_counts.csv"), 'w') as s:
		s.write("Image,ch1a,ch1s,Number_of_Particles\n")
	for ch1a in ch1a_arr:
		for ch1s in ch1s_arr:
			analysis(pa, ch1a, ch1s)
			time.sleep(1)
		
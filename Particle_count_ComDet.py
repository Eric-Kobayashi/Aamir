import os
import os.path as op
from ij import IJ
from ij import WindowManager as wm
import time

pa = "/Volumes/GoogleDrive/My Drive/Aamir/Aamir_McEwan Lab_GDrive/Lab Book - Aamir/Takeda_DDU/July 2019/SHSY5Y Electroporation/Raw Data 1_4 days/Day 3"
ch1a_arr = [3]
ch1s_arr = [40]

def analysis(pa, ch1a, ch1s):
	IJ.run("Close All", "")
	List_of_images = []
	flag = False
	try:
		for roots, dirs, files in os.walk(pa):
			for f in files:
				if f.endswith('.tif'):
					List_of_images.append(op.join(roots, f))
	except:
		List_of_images = wm.getImageTitles()
		flag = True
							
	List_of_results = []
	for tit in List_of_images:
		IJ.run("Clear Results")
		try:
			if flag:
				imp = wm.getImage(tit)
			else:
				imp = IJ.openImage(tit)
		except:
			print('No images detected!')
			continue

		try:
			IJ.redirectErrorMessages()
			IJ.run(imp, "Detect Particles", "ch1a={} ch1s={} add=Nothing".format(ch1a, ch1s))
		except:
			with open(op.join(pa, "summary.csv"), 'a') as s:
				contents = "0,0,0,0\n"
				s.write("{},{},{},{}".format(tit.replace(".tif", ""), ch1a, ch1s, contents))
			imp.close()
			continue
		
		IJ.selectWindow("Summary")
		result_path = op.join(pa, tit.replace(".tif", ".txt"))
		IJ.saveAs("text", result_path)
		List_of_results.append(result_path)

		with open(op.join(pa, "particle_counts.csv"), 'a') as s:
			with open(pa, 'r') as rf:
				for lines in rf:
					if 'Channel' not in lines:
						contents = ','.join(lines.split('\t'))
			s.write("{},{},{},{}".format(tit.replace(".tif", ""), ch1a, ch1s, contents))
		imp.close()
		
	for r in List_of_results:
		os.remove(r)
		
if __name__ in ["__main__", "__builtin__"]:
	with open(op.join(pa, "particle_counts.csv"), 'w') as s:
		s.write("Image,ch1a,ch1s,Channel,Slice,Frame,Number_of_Particles\n")
	for ch1a in ch1a_arr:
		for ch1s in ch1s_arr:
			analysis(pa, ch1a, ch1s)
			time.sleep(1)
		
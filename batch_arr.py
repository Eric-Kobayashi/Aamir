import os
import os.path as op
from ij import IJ
from ij import WindowManager as wm
import time

save_path = "/Volumes/GoogleDrive/My Drive/Aamir/Aamir_McEwan Lab_GDrive/Lab Book - Aamir/Takeda_DDU/July 2019/SHSY5Y Electroporation/Raw Data 1_4 days/Day 3"
image_path = save_path
ch1a_arr = [3]
ch1s_arr = [40]

def analysis(save_path, ch1a, ch1s, image_path):
	if image_path == 'NA':
		List_of_images = wm.getImageTitles()
	else:
		try:
			for roots, dirs, files in os.walk(image_path):
				for f in files:
					if f.endswith('.tif'):
						im = IJ.openImage(op.join(roots, f))
						im.show()
		except:
			return
		List_of_images = wm.getImageTitles()
							
	List_of_results = []
	for tit in List_of_images:
		IJ.run("Clear Results")
		try:
			imp = wm.getImage(tit)
		except:
			continue
		try:
			IJ.redirectErrorMessages()
			IJ.run(imp, "Detect Particles", "ch1a={} ch1s={} add=Nothing".format(ch1a, ch1s))
		except:
			with open(op.join(save_path, "summary.csv"), 'a') as s:
				contents = "0,0,0,0\n"
				s.write("{},{},{},{}".format(tit.replace(".tif", ""), ch1a, ch1s, contents))
			imp.close()
			continue
		
		IJ.selectWindow("Summary")
		result_path = op.join(save_path, tit.replace(".tif", ".txt"))
		IJ.saveAs("text", result_path)
		List_of_results.append(result_path)

		with open(op.join(save_path, "summary.csv"), 'a') as s:
			with open(result_path, 'r') as rf:
				for lines in rf:
					if 'Channel' not in lines:
						contents = ','.join(lines.split('\t'))

			s.write("{},{},{},{}".format(tit.replace(".tif", ""), ch1a, ch1s, contents))
		
		imp.close()
		
	for r in List_of_results:
		os.remove(r)
		
if __name__ in ["__main__", "__builtin__"]:
	if image_path == "":
		image_path = 'NA'
	with open(op.join(save_path, "summary.csv"), 'w') as s:
		s.write("Image,ch1a,ch1s,Channel,Slice,Frame,Number_of_Particles\n")
	for ch1a in ch1a_arr:
		for ch1s in ch1s_arr:
			analysis(save_path, ch1a, ch1s, image_path)
			time.sleep(1)


		
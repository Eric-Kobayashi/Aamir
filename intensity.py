import os
import os.path as op
from ij import IJ
from ij import WindowManager as wm
from ij.measure import ResultsTable as rt
import time

pa = r"F:\Dropbox (Cambridge University)\Artemisia\Aamir\Day3-DAPI\Tau"
minv_arr = [156]
maxv_arr = [248]

def measure_background(pa, minv_arr, maxv_arr):
	IJ.run("Set Measurements...", "mean display redirect=None decimal=3")
	IJ.run("Input/Output...", "jpeg=85 gif=-1 file=.txt use_file copy_column save_column");
	List_of_img = []
	IJ.run("Clear Results", "")
	for roots, dirs, files in os.walk(pa):
		for f in files:
			if f.endswith('.tif'):
				List_of_img.append(op.join(roots, f))
	for minv in minv_arr:
		for maxv in maxv_arr:
			for img in List_of_img:
				imp = IJ.openImage(img)
		#		imp.setDisplayRange(156, 248)
				imp.setDisplayRange(minv, maxv)
				IJ.run(imp, "Apply LUT", "")
				IJ.run(imp, "Measure", "")
				results = rt.getResultsTable()
				results.addValue('Min_value', minv)
				results.addValue('Max_value', maxv)
	result_path = op.join(pa, op.basename(pa)+'.csv')
	results.saveAs(result_path)
		
if __name__ in ["__main__", "__builtin__"]:
	measure_background(pa, minv_arr, maxv_arr)
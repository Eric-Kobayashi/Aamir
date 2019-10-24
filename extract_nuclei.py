from ij import IJ
from ij import WindowManager as wm
import ij.plugin.ZProjector as ZProjector
import ij.plugin.frame.RoiManager as RoiManager
from ij.plugin import Concatenator, ImageCalculator
import time
import os
import os.path as op
import shutil as sh
import sys
					
def generate_comp(pa, f):
	savedir = op.join(op.dirname(pa), "comps")
	mydir = op.join(pa, "threshold")
	if not op.isdir(mydir): os.mkdir(mydir)
	f_name = f.replace('.tif', '')
	if op.isfile(op.join(savedir, f_name+"_comp.tif")):
		return
	green = op.join(pa, f)
	ic = ImageCalculator()
	Huang = [2,3,3,3,4,4,4]
	for r in range(3, 10):
		IJ.run('Close All')
		imp = IJ.openImage(green)
		imp2 = imp.duplicate()
		imp2.setDisplayRange(523, 2075);
		IJ.run(imp2, "8-bit", "")
		IJ.run(imp2, "Subtract Background...", "rolling={}".format(r));
		x = Huang[r-3]
		IJ.setThreshold(imp2, x, 255, None)
		IJ.run(imp2, "Convert to Mask", "method=Default background=Dark black")
		imp3 = imp2.duplicate()
		IJ.run(imp3, "Fill Holes", "")
		imp4 = ic.run("Subtract create", imp3, imp2)
		IJ.run(imp4, "Analyze Particles...", "size=2-Infinity circularity=0.00-1.00 show=Masks clear include in_situ");
		imp4.setTitle("Nuclei")
		IJ.saveAs(imp4, "Tiff", op.join(mydir, "Nuclei_{}.tif".format(r)))
	List_of_imgs = []
	for t in os.listdir(mydir):
		if t.startswith('Nuclei'):
			List_of_imgs.append(op.join(mydir, t))

	flag = True
	for img in List_of_imgs:
		imp = IJ.openImage(img)
		if flag: 
			comb = imp.duplicate()
			flag = False
			continue
		comb = ic.run("OR create", comb, imp)
		
	for img in List_of_imgs:
		while True:
			try: 
				os.remove(img)
				break
			except OSError:
				pass
	 
	IJ.run(comb, "Analyze Particles...", "size=2-Infinity circularity=0.00-1.00 show=Masks clear include in_situ");
	IJ.run(comb, "16-bit", "")
	#IJ.saveAs(comb, "Tiff", op.join(savedir, f_name+"thresh.tif"))
	comb.setTitle("comb")
	comb.show()
	imp = IJ.openImage(green)
	imp.setTitle("green")
	imp.show()
	IJ.run("Merge Channels...", "c2=green c3=comb create");
	IJ.saveAs("Tiff", op.join(savedir, f_name+"_comp.tif"))
	IJ.run("Close All")
	
if __name__ in ['__main__', '__builtin__']:
	pa = r"F:\Dropbox (Cambridge University)\Artemisia\Aamir\Day 3-20191023T163847Z-001\Day 3\Green"
	for roots, dirs, files in os.walk(pa):
		for f in files:
			generate_comp(pa, f)
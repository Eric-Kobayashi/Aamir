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

# Path to image folder
pa = r"F:\Dropbox (Cambridge University)\Artemisia\Aamir\Day 3-20191023T163847Z-001\Day 4\Green"
	
def generate_comp(pa, f):
	savedir = op.join(op.dirname(pa), "comps")
	if not op.isdir(savedir): os.mkdir(savedir)
	mydir = op.join(pa, "threshold")
	if not op.isdir(mydir): os.mkdir(mydir)
	for f in os.listdir(mydir):
		os.remove(op.join(mydir, f))
	f_name = f.replace('.tif', '')
#	if op.isfile(op.join(savedir, f_name+"_comp.tif")):
#		return
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
	imp, seeds_num = extract_seeds(green, mydir)
	imp.setTitle("seeds")
	imp.show()
	g = IJ.openImage(green)
	g.setTitle("Venus-tau")
	g.show()
	IJ.run("Merge Channels...", "c1=seeds c2=Venus-tau c3=comb create");
	IJ.saveAs("Tiff", op.join(savedir, f_name+"_comp.tif"))
	IJ.run("Close All")
	return seeds_num

def extract_seeds(imgpath, mydir):
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager()
	rm.reset()
	imp = IJ.openImage(imgpath)
	IJ.run(imp, "Detect Particles", "  ch1a=3 ch1s=125 add=[All detections]")
	ave_imp = ZProjector.run(imp, "avg")
	stats = ave_imp.getStatistics(0x10000).median
	bg_8bit = int(round(stats*1.0/256))
	IJ.setBackgroundColor(bg_8bit, bg_8bit, bg_8bit)
	imp.setDisplayRange(0, 65535)
	nroi = rm.getCount()
	if nroi == 0:
		IJ.run(imp, "Select All", "")
		IJ.run(imp, "Clear", "stack")
	elif nroi == 1:
		rm.select(imp, 0)
		IJ.run(imp, "Clear Outside", "stack")
	else:
		rm.setSelectedIndexes(range(nroi))
		rm.runCommand(imp, "Combine")
		IJ.run(imp, "Clear Outside", "stack")
	return imp, nroi

def generate_sum(pa, n_tif, num_seeds_dict):
	groovy_path = op.join(op.dirname(pa), "RunMe.groovy")
	cell_quant = op.join(op.dirname(pa), "cell_quant")
	if not op.isdir(cell_quant):
		os.mkdir(cell_quant)
	with open(groovy_path, 'w') as g:
		g.write('''def imagename = getCurrentServer().getPath().split('/').last().replace('.tif', '')
setImageType('FLUORESCENCE');
createSelectAllObject(true);
runPlugin('qupath.imagej.detect.cells.PositiveCellDetection', '{{"detectionImage": "Channel 3",  "backgroundRadius": 0.0,  "medianRadius": 1.0,  "sigma": 1.5,  "minArea": 20.0,  "maxArea": 100.0,  "threshold": 100.0,  "watershedPostProcess": true,  "cellExpansion": 5.0,  "includeNuclei": true,  "smoothBoundaries": true,  "makeMeasurements": true,  "thresholdCompartment": "Cell: Channel 1 max",  "thresholdPositive1": 2000.0,  "thresholdPositive2": 200.0,  "thresholdPositive3": 300.0,  "singleThreshold": true}}');
saveDetectionMeasurements(String.format('/{}/%s_det.txt', imagename));'''.format(cell_quant.replace(op.sep, '/')))
	print('Please run groovy script in QuPath')
	
	while True:
		list_of_quant = []
		for roots, dirs, files in os.walk(cell_quant):
			for f in files:
				if f.endswith('det.txt'):
					list_of_quant.append((roots, f))
		if len(list_of_quant) < n_tif:
			time.sleep(2)
			if len(list_of_quant) > 0:
				print('QuPath progress: {0:.1f}%'.format(len(list_of_quant)*100.0/n_tif))
		else: break

	summary = op.join(op.dirname(pa), op.basename(op.dirname(pa))+'.csv')
	with open(summary, 'w') as s:
		s.write("Image,Positive_cell,Negative_cell,Total_cell,Positive_percentage,Number_of_seeds\n")
		for r, q in list_of_quant:
			pos = neg = 0
			img_id = q.replace('_comp_det.txt', '')
			with open(op.join(r, q), 'r') as quant:
				for lines in quant:
					if 'Positive' in lines[:20]:
						pos += 1
					elif 'Negative' in lines[:20]:
						neg += 1
			cells = pos+neg
			if cells == 0:
				s.write("{},0,0,0,0,{}\n".format(img_id, num_seeds_dict[img_id]))
			else:
				s.write("{},{},{},{},{},{}\n".format(img_id, pos, neg, cells, pos*100.0/cells, num_seeds_dict[img_id]))


if __name__ in ['__main__', '__builtin__']:
	List_of_tif = []
	seeds = {}
	for roots, dirs, files in os.walk(pa):
		for f in files:
			if f.endswith('m.tif'):
				List_of_tif.append((roots, f))
	n = len(List_of_tif)
	print("{} images found.".format(n))
	i = 0
	for r, f in List_of_tif:
		s = generate_comp(r, f)
		seeds[f.replace('.tif','')] = s
		i += 1
		print('ImageJ progress: {0:.1f}%'.format(i*100.0/n))
		
	# Do qupath cell identification and save summary
	generate_sum(pa, n, seeds)
	print('Script finished.')
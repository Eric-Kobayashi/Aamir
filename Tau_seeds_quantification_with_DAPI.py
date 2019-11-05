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
pa = r"F:\Dropbox (Cambridge University)\Artemisia\Aamir\Day3-DAPI"
ch1a = 3   # pixel size
ch1s = 125 # threshold
	
def combine_DAPI(pa):
	List_of_tif = []
	savedir = op.join(pa, "comps")
	if not op.isdir(savedir): os.mkdir(savedir)
	for roots, dirs, files in os.walk(op.join(pa, 'Tau')):
		for f in files:
			if f.endswith('.tif'):
				List_of_tif.append((roots, f))
	n = len(List_of_tif)
	print("{} images found.".format(n))
	i = 0
	seeds = {}
	for r, f in List_of_tif:
		green = op.join(r, f)
		f_name = f.replace('.tif','').replace(' ','_')
		dapi = op.join(r.replace('Tau', 'DAPI'), f.replace('Blue - FITC', 'UV - DAPI'))
		assert op.isfile(dapi), "Please check file names!"
		imp, seeds_num = extract_seeds(green)
		imp.setTitle("seeds")
		imp.show()
		g = IJ.openImage(green)
		g.setTitle("Venus-tau")
		g.show()
		d = IJ.openImage(dapi)
		d.setTitle("dapi")
		d.show()
		IJ.run("Merge Channels...", "c1=seeds c2=Venus-tau c3=dapi create");
		IJ.saveAs("Tiff", op.join(savedir, f_name+"_comp.tif"))
		IJ.run("Close All")
		seeds[f_name] = seeds_num
		i += 1
		print('ImageJ progress: {0:.1f}%'.format(i*100.0/n))
	return seeds, n
	
def extract_seeds(imgpath):
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager()
	rm.reset()
	imp = IJ.openImage(imgpath)
	IJ.redirectErrorMessages()
	try:
		IJ.run(imp, "Detect Particles", "  ch1a={} ch1s={} add=[All detections]".format(ch1a, ch1s))
	except:
		print("No particle detected in {}".format(imgpath))
	ave_imp = ZProjector.run(imp, "avg")
	stats = ave_imp.getStatistics(0x10000).median
	bg_8bit = int(round(stats*1.0/256))
	IJ.setBackgroundColor(bg_8bit, bg_8bit, bg_8bit)
	imp.setDisplayRange(0, 65535)
	nroi = rm.getCount()
	if nroi >= 0:
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
	groovy_path = op.join(pa, "RunMe.groovy")
	cell_quant = op.join(pa, "cell_quant")
	qupath_project = op.join(pa, "qupath_project")
	if op.isdir(qupath_project):
		sh.rmtree(qupath_project)
	os.mkdir(qupath_project)
	if not op.isdir(cell_quant):
		os.mkdir(cell_quant)
	with open(groovy_path, 'w') as g:
		g.write('''def imagename = getCurrentServer().getPath().split('/').last().replace('.tif', '')
setImageType('FLUORESCENCE');
createSelectAllObject(true);
runPlugin('qupath.imagej.detect.cells.PositiveCellDetection', '{{"detectionImage": "Channel 3",  "requestedPixelSizeMicrons": 0.5,  "backgroundRadiusMicrons": 0.0,  "medianRadiusMicrons": 1.0,  "sigmaMicrons": 1.0,  "minAreaMicrons": 20.0,  "maxAreaMicrons": 300.0,  "threshold": 2000.0,  "watershedPostProcess": true,  "cellExpansionMicrons": 5.0,  "includeNuclei": true,  "smoothBoundaries": true,  "makeMeasurements": true,  "thresholdCompartment": "Cell: Channel 1 max",  "thresholdPositive1": 2000.0,  "thresholdPositive2": 200.0,  "thresholdPositive3": 300.0,  "singleThreshold": true}}');
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

	summary = op.join(pa, op.basename(pa)+'.csv')
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
	seeds, n = combine_DAPI(pa)
	# Do qupath cell identification and save summary
	generate_sum(pa, n, seeds)
	print('Script finished.')
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

def move_WL_images(pa):
    L = []
    for roots, dirs, files in os.walk(pa):
        for f in files:
            if '.path.txt' in f:
                L.append((roots, f))
                
    for r, f in L:
    	with open(op.join(r, f)) as pathfile:
    		tiff_path = pathfile.read()
        wl_path = tiff_path.replace('Aptamer_561','WL')
        wl_img = IJ.openVirtual(wl_path)
        ave_wl = ZProjector.run(wl_img, 'avg')
        IJ.saveAs(ave_wl, "Tiff", op.join(r, 'WL_ave_img.tiff'))
        wl_img.close()
        ave_wl.close()

def deselect_FOVs(pa):
	List_of_tif = []
	for roots, dirs, files in os.walk(pa):
		for f in files:
			if 'trimmed.tif' in f:
				List_of_tif.append((roots, f))

	for r, f in List_of_tif:
		imp = IJ.openImage(op.join(r, f))
		IJ.run(imp, "Select None", "")
		IJ.save(imp, op.join(r, f))
		imp.close()

def create_concat(pa):
	List_of_dir = []
	for roots, dirs, files in os.walk(pa):
		for f in files:
			if '561.tif' in f:
				List_of_dir.append(roots) 
	
	List_of_dir = list(set(List_of_dir))
	
	for d in List_of_dir:
		List_of_tif = []
		for tif in os.listdir(d):
			if '561.tif' in tif:
				List_of_tif.append(op.join(d, tif))
		List_of_img = [IJ.openImage(t) for t in List_of_tif]
		concat = Concatenator.run(List_of_img)
		IJ.saveAs(concat, "Tiff", op.join(d, "concat.tif"))
		concat.close()

def create_image_pixel_average(pa):
	L = []
	for roots, dirs, files in os.walk(pa):
		for f in files:
			if f == 'concat.tif':
				L.append((roots, f))  
	for r, f in L:
		pathfile = os.path.join(r, f)	
		imp = IJ.openImage(pathfile)
		IJ.run(imp, "Hyperstack to Stack", "")
		ave_imp = ZProjector.run(imp, "avg")
		ave_imp.show()
		IJ.run("Set Scale...", "distance=1 known=98.6 pixel=1 unit=nm")
		IJ.run("Measure")
		IJ.selectWindow("Results")
		IJ.saveAs("Results", op.join(r, "average_intensity.txt"))
		IJ.run("Clear Results", "")
		IJ.run("Close All", "")

def create_intensity_profile(pa, result_pa):
	List_of_tracks = []
	i = 0
	with open(pa, 'r') as track_file:

		for lines in track_file:
			if i == 0: 
				i += 1
				continue
			a_ID = ''.join(lines.split(',')[0].split('_')[2:])
			c_ID = int(lines.split(',')[1])
			p = op.dirname(a_ID)
			List_of_tracks.append((p, c_ID))
			
	for p, c_ID in List_of_tracks:
		folder = p.split('\\')[-3] + '_' + p.split('\\')[-2]
		result_f = op.join(result_pa, folder)
		if not op.isdir(result_f):
			os.makedirs(result_f)
		roi_file = op.join(p, "clusters_roi.txt")
		assert op.isfile(roi_file)

		with open(op.join(p, "raw_img_concat.path.txt")) as raw_img:
			img = raw_img.read()
		if not op.isfile(img):
			img = img.replace(r"Group\\Rohan\\", r"Group\\Rohan\\20190205\\")

		assert op.isfile(img)
		imp = IJ.openVirtual(img)
		
		rm = RoiManager.getInstance()
		if not rm:
			rm = RoiManager()
		rm.reset()
		i = 0
		with open(roi_file) as roi_f:
			for lines in roi_f:
				if i < c_ID: 
					i += 1
					continue
				else:
					coord = lines[:-1].split(',')
					x, y = int(coord[0]) / 8 - 1, int(coord[1]) / 8 - 1
					if x < 0: x += 1
					if y < 0: y += 1
					w, l = 2, 2
					eval("imp.setRoi({})".format(','.join([x, y, w, l])))
					break
		IJ.run(imp, "Plot Z-axis Profile", "")
		imp.killroi()
		IJ.saveAs(wm.getCurrentImage(), "Tiff", op.join(result_f, "track_{}.tiff".format(c_ID)))
					
def test_para(pa):
	ic = ImageCalculator()
	for r in [5]: # ,10,15,20,25,30
		for m in ["Bernsen"]: # ,"Contrast","Mean","Median","MidGrey","Niblack","Otsu","Phansalkar","Sauvola"
			for dilate in [1, 0]:
				IJ.run('Close All')
				imp = IJ.openImage(op.join(pa, "F - 11(fld 7 wv Blue - FITC).tif"))
				tarimg = IJ.openImage(op.join(pa, "F - 11(fld 7 wv UV - DAPI).tif"))
				IJ.run(tarimg, "Make Binary", "")
				tarimg.setTitle("Target")
				imp2 = imp.duplicate()
				IJ.run(imp2, "8-bit", "")
				#IJ.run(imp2, "Auto Threshold", "method={} white".format(r));
				IJ.run(imp2, "Auto Local Threshold", "method={} radius={} parameter_1=0 parameter_2=0 white".format(m, r))
				imp3 = imp2.duplicate()
				IJ.run(imp3, "Fill Holes", "")
				imp4 = ic.run("Subtract create", imp3, imp2)
				if dilate: IJ.run(imp4, "Dilate", "")
				imp4.setTitle("Nuclei")
				tarimg.show()
				imp4.show()
				IJ.run("Label Overlap Measures", "source=Nuclei target=Target jaccard")
				wm.setWindow(wm.getWindow("Nuclei-all-labels-overlap-measurements"))
				IJ.saveAs("Results", op.join(pa, "Jaccard_{}_{}_{}.txt".format(m, r, dilate)))
	List_of_results = []
	for t in os.listdir(pa):
		if t.startswith('Jaccard'):
			List_of_results.append(t)

	with open(op.join(pa, "Results.csv"), 'w') as r:
		r.write("Method,Radius,Dilate,Jaccard\n")
		for l in List_of_results:
			with open(op.join(pa, l), 'r') as ind:
				r.write("{},{},{},{}\n".format(l.replace('.txt', '').split('_')[1:],float(ind.readlines()[1][:-1])))
			time.sleep(0.1)
			os.remove(op.join(pa, l))
	IJ.run("Close All")
		
	
if __name__ in ['__main__', '__builtin__']:
	pa = r"C:\Users\Eric\Documents\Github\Aamir"
	test_para(pa)
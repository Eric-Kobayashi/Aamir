import qupath.lib.projects.Projects;
import java.awt.image.BufferedImage;
import qupath.lib.images.servers.ImageServerBuilder.ServerBuilder;
import java.net.URI;
import java.io.File;

File d = new File("D:/Tau_Venus_Costar_mice_Akis_Aamir_1/qu");
img = "D:\Tau_Venus_Costar_mice_Akis_Aamir_1\comps\A_-_01(fld_1_wv_Blue_-_FITC)_comp.tif"
q = getQuPath();
p = Projects.createProject(d, BufferedImage.class)
q.setProject(p);

p.addImage(

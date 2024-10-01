#first add a dataset to omero!! Can do this right on the omero website.

conda activate omero
omero -s omero.nyumc.org -u mh6486 login
omero import -d 24225 0413-3D_1018924.ome.tiff
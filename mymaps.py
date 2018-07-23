from editor.mapbuilding import MapInitializer

#Here I simply define some properties of differnt maps. No programmation, just
#configuration.

#For a description of each parameter, please go the file editor/mapbuilding.py
#and have a look at the MapInitializer constructor

demo_map1 = MapInitializer("First demo map")

demo_map2 = MapInitializer("Second demo map")
demo_map2.world_size = (256, 128) #with big maps it is better to use lower persistance
demo_map2.persistance = 1.3 #The higher, the bigger are the "continents"
demo_map2.palm_homogeneity = 0.9
demo_map2.chunk = (10000,0)


demo_map3 = MapInitializer("Huge, third demo map")
demo_map3.world_size = (512,512) #with big maps it is better to use lower persistance
demo_map3.zoom_cell_sizes = [12]




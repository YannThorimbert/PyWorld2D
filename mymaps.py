from editor.mapbuilding import MapInitializer

#Here I simply define some properties of differnt maps. No programmation, just
#configuration.

#For a description of each parameter, please go the file editor/mapbuilding.py !

demo_map1 = MapInitializer("First Map Demo")

demo_map2 = MapInitializer("Second Map Demo")
demo_map2.world_size = (256, 64)
demo_map2.persistance = 0.85 #The higher, the bigger are the "continents"
demo_map2.palm_homogeneity = 0.9
demo_map2.chunk = (0,0)



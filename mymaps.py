from editor.mapbuilding import MapInitializer

#Here I simply define some properties of differnt maps. No programmation, just
#configuration.

#For a description of each parameter, please go the file editor/mapbuilding.py !

demo_map1 = MapInitializer("First Map Demo")

demo_map2 = MapInitializer("Second Map Demo")
demo_map2.world_size = (256, 128) #with big maps it is better to use lower persistance
demo_map2.persistance = 1.3 #The higher, the bigger are the "continents"
demo_map2.palm_homogeneity = 0.9
demo_map2.chunk = (10000,0)



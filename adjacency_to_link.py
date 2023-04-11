f_in = open("adjacency_list_old.txt", "r")
f_out = open("link.txt", "w")
lines = f_in.readlines()
for line in lines:
    names = line.split('|')
    for i in range(1,len(names)):
        # Run for each name except first name
        f_out.write('["'+names[0].replace('\n','')+'", "'+names[i].replace('\n','')+'"],\n')
f_in.close()
f_out.close()
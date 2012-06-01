from subprocess import call

#Temporary file.

def renderGraph(dataFile, propertyFile, outputFile, afPath, afArgs):
    
    return call("./afterglow.sh " + dataFile + " " + propertyFile + " " + 
                outputFile + " " + afPath + " " + afArgs, shell=True)

    
#Check if method is okay.
print renderGraph("firewall.csv", "sample.properties", "test123.gif", "afterglow.pl", "-e 1.5 -d")

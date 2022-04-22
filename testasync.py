from sys import argv
sid = argv[2]
link = argv[1]

fichier = open(f"temp_subprocess_output/{sid}.json", "a")
fichier.write( "{"+ f'"link":"{link}"' +"}")
fichier.close()

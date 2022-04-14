import sys
sid = sys.argv[2]
link = sys.argv[1]

fichier = open(f"temp_subprocess_output/{sid}.json", "a")
fichier.write( "{"+ f'"link":"{link}"' +"}")
fichier.close()
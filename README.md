##To run the report manually

$ bash run-report.sh

You may see some error output when the description contains funky characters.  
These bugs are dropped from the report, so I usually manualy fix the bug titles 
for the next run.  Such errors look like the following


'ascii' codec can't encode character u'\u2019' in position 160: ordinal not in range(128) ,{"index": 930, "id": 1352193, "importance": "Undecided", "status": "New", "owner": "https://api.launchpad.net/1.0/~dbcocle", "title": "The nova API service can’t hand image metadata properly when metadata key contains uppercase letter", "link": "https://bugs.launchpad.net/nova/+bug/1352193","age": 31, "update": 29, "stale": 0, "never_touched": 0,"projects": [{"target": "nova", "status": "New"}] ,"reviews": []}


Once the report is done (it takes about 1/2 hour currently), you need to rename the output 
file from bugs_refresh.json to bugs.json.  Then you can use your handy brower to 
open the nova-bugs.html file and you should see the page and the new data.

##Licensing
This Project is licensed under the Apache License, Version 2.0 (the "License")

# TwitterStatic aka twitter-sync
Python command-line script to download (or sync) and create markdown copy of tweets older than X (e.g. for static sites).

Note, assumes Python3 (but may be backward compatible).

Dependency on Twitter library - please either install this as a full package via "pip install twitter-sync" or at least the dependency https://github.com/bear/python-twitter via "pip install python-twitter").

Btw, keep your libraries updated (eg great for loop @ https://stackoverflow.com/questions/47071256/how-to-update-upgrade-a-package-using-pip).

Once installed, use sample from https://github.com/ILAsoft/TwitterStatic/blob/master/TwitterSyncSettings.sample to create TwitterSyncSettings.ini one folder above your site's folder and then run "TwitterSync.py" from the website's folder itself.
# TwitterStatic aka twitter-sync
Python command-line script to automatically download and create markdown copy of all or subset of tweets (and keep in sync going forward). Ideal for making a replicate on a static site.
Uses combination of Twitter's own API and Nitter.net to iterate through and parse clean body of messages.

Available as a direct install, e.g. _pip install twitter-sync_

Dependency on Twitter library - if not doing a full package installation above, make sure to install the dependency https://github.com/bear/python-twitter via "pip install python-twitter".

Once installed, use sample from https://github.com/ILAsoft/TwitterStatic/blob/master/TwitterSyncSettings.sample to create TwitterSyncSettings.ini one folder above your site's folder and then run "TwitterSync.py" from the website's folder itself. Feel free to add appropriate styles to your website if you want to adjust the look and feel of the "tweets".
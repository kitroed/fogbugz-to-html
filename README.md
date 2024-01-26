## FogBugz to HTML

Quick commit of the mishmash pile of python etc. that I used to "download" the pages of my workplace's fogbugz.com instance. Start in `fogbuz_to_html.py` if you're ready for the madness, I also attempted to keep a TODO list in `html_scraping_steps.md`.

In short, I used `playwright` to run a Chrome(ium) instance that opened each FogBugz case page and downloaded the rendered html. I then used Beautiful Soup 4 (soup_fogbugz_html.py) to read the downloaded page and strip out all the unwanted bits.

I created SQLite files to help figure out what was in the bits I wanted to keep, made janky csv files full of poor-man's enumerators (i.e `avatars.csv`, `attachments.csv`, `wikis.csv` and so on...) which powered some of the soup logic.

I did a pass for grabbing the wiki HTML and attachment files directly out of an old SQL 2008 R2 backup copy (see the `.linq` files) that Fog Creek would still send you if you asked nicely, but then I realized that using the API was a better way to go (see `download_fogbugz_attachements.py` and `download_fogbugz_wiki.py`). I also grabbed a ton of the json that the API put out while I was at it (`download_fogbugz_case_json`).

I manually grabbed and trimmed down the stylesheets and they were manually renamed and re-referenced, so this isn't considered portable or particularly reusable. I tried to clear out any personally identifiable parts like API keys, usernames, or passwords. It was a fun multi-hour project that I wanted to keep the bits around in case I wanted to look at it again.

Kit Roed \
Jan 2024

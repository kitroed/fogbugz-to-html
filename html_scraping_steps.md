# HTML Scraping steps

## Rebuilding Case Page Steps

1. Rebuild `!DOCTYPE`, `<html>`, `<head>` from a template
2. insert title from original soup
3. `<body>` tag (no need for class?)
4. keep `<div id="main-wrap">` and all contents
5. delete `<div id="top-notifications">` (optional)
6. delete `<div class="drop-mask hidden">`
7. delete `<div id="case-errors-container">`
8. delete inner html of `<nav class="clear">` (twice)
9. delete `<label id="sidebarCorrespondent"`
10. delete `<label id="sidebarReleaseNotes"`
11. delete `<span class="rss field">`
12. delete `<div id="sidebarSubscribe">`
13. delete `<button class="m-btn working-on-case"`
14. delete inner html of `<span class="right-event-action-wrapper">`
15. delete `<div class="drop-mask hidden">`
16. delete `<div id="case-errors-container">`
17. delete `<div id="sidebar-outline">`

## URL rewrite steps

### `a` & `href`

1. if the scheme and netloc `http://fogbugz` rewrite to `//<fogbugz-instance-name>.fogbugz.com` and continue
2. if the netloc is `<fogbugz-instance-name>.fogbugz.com`
   1. If it has querystring value of `ixAttachment` (not equal to 0) download (check if already exists) as `./attachments/<attachment number>/<sFilename value>` and rewrite url
      1. if `ixAttacment` is 0, it's most likely the 32px kiwi.png, so saving as `./attachments/0/Kiwi.png`
   2. If it has querystring value of `ixBug` unwrap
   3. If it has path starting in `/f/cases/<case number>/` replace with `<case number>.html` (and keep anchor reference [fragment identifier])
   4. If it has path starting in `/f/filter`, unwrap
   5. If it's a user activity link, unwrap.
   6. If it's `default.asp?W<Number>` it's a wiki, link to `wikis/<Wiki Name>/W<number><article name>.html` _how_?
      1. Idea is to set up a lookup table, c1 `W<number>` c2, full path (done as csv)


### `img`

1. link to attachment file if `ixAttachment` is found in querystring, otherwise leave as-is?
2. if the netloc is `attachment.freshservice.com` try to download? (there are 22 in img src)
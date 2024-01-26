// similar to the LINQPad script used to extract the attachment binaries, 
// this grabs the stored wiki articles from a restored copy of the fogbugz database.

string RemoveInvalidFilePathCharacters(string filename, string replaceChar)
{
	string regexSearch = new string(Path.GetInvalidFileNameChars()) + new string(Path.GetInvalidPathChars());
	Regex r = new Regex(string.Format("[{0}]", Regex.Escape(regexSearch)));
	return r.Replace(filename, replaceChar);
}
// we're going to put all of the W articles into a folder with the name of the "Wiki" they were in
// these were called Wikis (top-level wiki?), also using a different top-level folder to indicate if the wiki was deleted.
var wikiArticles = from wp in WikiPages
					join w in Wikis on wp.IxWiki equals w.IxWiki
					select new { wikiName = w.SWiki, w.FDeleted, wp.IxWikiPage, wp.SHeadline, wp.SBody };

string savePath;

foreach (var wa in wikiArticles)
{
	savePath = (wa.FDeleted == 1 ? @"D:\deleted_wikis\" : @"D:\wikis\");
	if (!Directory.Exists(savePath + RemoveInvalidFilePathCharacters(wa.wikiName, "-")))
	{
		Directory.CreateDirectory(savePath + RemoveInvalidFilePathCharacters(wa.wikiName, "-"));
	}
	if (wa.SBody.Length > 0)
	{
		File.WriteAllText(savePath
			+ RemoveInvalidFilePathCharacters(wa.wikiName, "-") + @"\W"
			+ wa.IxWikiPage.ToString() + " "
			+ RemoveInvalidFilePathCharacters(wa.SHeadline, "-") + ".html",
			"<h1>" + wa.SHeadline + "</h1>\n\n" + wa.SBody, Encoding.UTF8);
	}
}

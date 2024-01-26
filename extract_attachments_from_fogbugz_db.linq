// this was run in LINQPad on a restored copy of the fogbugz database circa 2019 
// around which time, they quit storing attachments in the database anyway,
// but I'm including this because I thought it was clever :)

string RemoveInvalidFilePathCharacters(string filename, string replaceChar)
{
	string regexSearch = new string(Path.GetInvalidFileNameChars()) + new string(Path.GetInvalidPathChars());
	Regex r = new Regex(string.Format("[{0}]", Regex.Escape(regexSearch)));
	return r.Replace(filename, replaceChar);
}

var all_attachments = from att in Attachments
					  select att;

string savePathRoot = @"attachments\";

foreach (var attachment in all_attachments)
{
	if (!Directory.Exists(savePathRoot + attachment.IxAttachment.ToString()))
	{
		Directory.CreateDirectory(savePathRoot + attachment.IxAttachment.ToString());
	}
	try
	{
		File.WriteAllBytes(savePathRoot + attachment.IxAttachment.ToString() + @"\" + ((attachment.SFilename.Length > 0) ? attachment.SFilename : "file"), attachment.SData.ToArray());
	}
	catch {
		(attachment.IxAttachment.ToString() + " " + attachment.SFilename.Dump()).Dump();
		File.WriteAllBytes(savePathRoot + attachment.IxAttachment.ToString() + @"\" + RemoveInvalidFilePathCharacters(attachment.SFilename, "_"), attachment.SData.ToArray());
		RemoveInvalidFilePathCharacters(attachment.SFilename, "_").Dump();
	}
}

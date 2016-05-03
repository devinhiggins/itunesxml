## iTunes XML Processor

Create a csv file of your iTunes listening history, suitable for deployment at [Universal Scrobbler](http://universalscrobbler.com/index.php). Note, however, that last.fm rejects any scrobbles older than ~13 days, disallowing the addition of historical listening history and somewhat defeating the purpose of this tool. Nevertheless, it may come in hand for future use, and can be adapted to create non-timestamped listen counts.

### Command line usage

usage: `itunesxml.py [-h] [-o output_format] path_to_xml`

*Extract play count data from iTunes XML library data*.

positional arguments:
  path_to_xml           Path to valid iTunes library XML file.

optional arguments:
  -h, --help            show this help message and exit
  -o, --output          output_format
                        Desired output format.


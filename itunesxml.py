"""Extract play-count information form itunes xml."""
from lxml import etree
import argparse
import sys
from tqdm import tqdm
import csv
from pprint import pprint
import os
from datetime import datetime


class ItunesXml(object):
    """Object to interact with itunes xml."""

    def __init__(self, path):
        """Open itunes xml file."""
        self.path = path

    def extract_plays(self, output=None):
        """Extract play information from xml.

        kwargs:
            output(str): format to deliver results in; currently
                only accepted value is csv.
        """
        self.output = output
        self.play_count_data = []
        self._load_xml()

    def _build_csv(self):
        """Use list of song data to generate scrobble-friendly csv."""
        self.csv = []
        for record in tqdm(self.play_count_data):
            if self._unplayed(record):
                pass
            else:
                self.csv += self._get_row_data(record)
        # pprint(self.csv[0:6])
        self._store_csv()

    def _store_csv(self):
        csv_path = self._get_csv_path()
        with open(csv_path, "w") as csvfile:
            fieldnames = ["artist", "song", "album",
                          "timestamp", "album_artist", "duration"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for row in tqdm(self.csv):
                writer.writerow(row)
        print("Wrote file at {0}".format(csv_path))

    def _get_csv_path(self):
        """Store csv file next to source xml."""
        return os.path.splitext(self.path)[0] + ".csv"

    def _unplayed(self, record):
        """Check if song has been played.

        args:
            record(dict): full record for a given song
        """
        return "Play Count" not in record or record.get("Play Count", "0") == "0"

    def _get_row_data(self, record):
        """Produce rows for each play of the supplied track.

        args:
            record(dict): all track data
        """
        rdata = []
        artist = record.get("Artist", "")
        album_artist = record.get("Album Artist", "")
        song = record["Name"]
        album = record.get("Album", "")
        play_count = record["Play Count"]
        duration = int(record["Total Time"]) / 1000
        last_play = record["Play Date UTC"]
        date_added = record["Date Added"]
        playtimes = self._get_playtimes(date_added, last_play, int(play_count))
        for playtime in playtimes:
            playdata = {"artist": artist,
                        "song": song,
                        "album": album,
                        "timestamp": playtime,
                        "album_artist": album_artist,
                        "duration": duration
                        }
            rdata.append(playdata)
        return rdata

    def _get_playtimes(self, add_date, play_date, plays):
        """Get play dates for tracks.

        Play times will be generated using average interval
        between date the track was added and its most recent play.

        args:
            add_date(str): UTC formatted date string
            play_date(str): UTC formatted date string
            plays(int): play count
        """
        play_date = datetime.strptime(play_date, "%Y-%m-%dT%H:%M:%SZ")
        if plays == "1":
            playtimes = [datetime.strftime(play_date, "%Y-%m-%d %H:%m:%S")]
        else:
            add_date = datetime.strptime(add_date, "%Y-%m-%dT%H:%M:%SZ")
            # Split plays evenly over elapsed time between adding tack and most
            # recent play.
            interval = (play_date - add_date) / plays
            playtimes = []
            for i in range(plays):
                play_time = add_date + interval * (i + 1)
                playtimes.append(datetime.strftime(play_time, "%Y-%m-%d %H:%m:%S"))
        return playtimes

    def _load_xml(self):
        """Begin xml pipeline."""
        self._xml = etree.parse(self.path)
        print("Loading XML...")
        self._load_songs()

    def _load_songs(self):
        """Find and load song trees."""
        self._songs = self._xml.xpath("/plist/dict/dict/dict")
        self._process_songs()

    def _process_songs(self):
        """Iterate through songs."""
        print("Processing songs...")
        for song in tqdm(self._songs):
            self._song_data = {}
            self._process_song(song)
            self.play_count_data.append(self._song_data)
        print("Found data for {0} songs".format(len(self.play_count_data)))
        # pprint(self.play_count_data[0])
        self._build_output()

    def _build_output(self):
        """Output results to user."""
        if self.output == "csv":
            self._build_csv()

    def _process_song(self, song):
        """Process individual song data.

        args:
            song(etreeElement): lxml Element type of the song level,
                including descendents.
        """
        for elem in song.iterchildren():
            self._process_element(elem)

    def _process_element(self, elem):
        """Isolate and store element.

        Each elem should have a tag named either 'key' or the format of data
        stored in the value described by the key. See xml sample below for details.

        args:
            elem(etreeElement): tree for each
        """
        if elem.tag == "key":
            self._current_key = elem.text
        else:
            value = elem.text
            self._song_data[self._current_key] = value


def process_args(args=None):
    """Process command line arguments from user.

    kwargs:
        args(list): list of args passed by user.
    """
    desc = "Extract play count data from iTunes XML library data."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("path_to_xml",
                        help="Path to valid iTunes library XML file.",
                        metavar="path_to_xml")
    parser.add_argument("-o", "--output",
                        help="Desired output format.",
                        default=None,
                        dest="output_format",
                        metavar="output_format",
                        choices=["csv"])
    return parser.parse_args(args)


if __name__ == "__main__":
    arg = process_args(sys.argv[1:])
    ixml = ItunesXml(arg.path_to_xml)
    ixml.extract_plays(output=arg.output_format)


# XML Data Sample

"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Major Version</key><integer>1</integer>
    <key>Minor Version</key><integer>1</integer>
    <key>Date</key><date>2011-12-14T06:49:42Z</date>
    <key>Application Version</key><string>10.5.1</string>
    <key>Features</key><integer>5</integer>
    <key>Show Content Ratings</key><true/>
    <key>Music Folder</key><string>file://localhost/C:/Users/Devin/Music/</string>
    <key>Library Persistent ID</key><string>CBE4B2A8B3CCB499</string>
    <key>Tracks</key>
    <dict>
        <key>4138</key>
        <dict>
            <key>Track ID</key><integer>4138</integer>
            <key>Name</key><string>Warped Mind</string>
            <key>Artist</key><string>Shed</string>
            <key>Album Artist</key><string>va</string>
            <key>Album</key><string>Berghain 02 Part I</string>
            <key>Grouping</key><string>ostgut tonträger</string>
            <key>Genre</key><string>Techno</string>
            <key>Kind</key><string>MPEG audio file</string>
            <key>Size</key><integer>17639662</integer>
            <key>Total Time</key><integer>432875</integer>
            <key>Year</key><integer>2008</integer>
            <key>Date Modified</key><date>2009-05-30T00:09:46Z</date>
            <key>Date Added</key><date>2009-05-26T05:12:24Z</date>
            <key>Bit Rate</key><integer>320</integer>
            <key>Sample Rate</key><integer>44100</integer>
            <key>Play Count</key><integer>5</integer>
            <key>Play Date</key><integer>3401878234</integer>
            <key>Play Date UTC</key><date>2011-10-19T20:10:34Z</date>
            <key>Skip Count</key><integer>1</integer>
            <key>Skip Date</key><date>2009-12-23T20:32:51Z</date>
            <key>Artwork Count</key><integer>1</integer>
            <key>Persistent ID</key><string>BB925F8B0C12246C</string>
            <key>Track Type</key><string>File</string>
            <key>Location</key><string>file://localhost/mind.mp3</string>
            <key>File Folder Count</key><integer>-1</integer>
            <key>Library Folder Count</key><integer>-1</integer>
        </dict>
"""

# Individual Output (Python Dict)

"""
{'Album': 'Berghain 02 Part I',
 'Album Artist': 'va',
 'Artist': 'Shed',
 'Artwork Count': '1',
 'Bit Rate': '320',
 'Date Added': '2009-05-26T05:12:24Z',
 'Date Modified': '2009-05-30T00:09:46Z',
 'File Folder Count': '-1',
 'Genre': 'Techno',
 'Grouping': 'ostgut tonträger',
 'Kind': 'MPEG audio file',
 'Library Folder Count': '-1',
 'Location': 'file://localhost/D:/music/Music/va/Berghain%2002%20Part%20I/Warped%20Mind.mp3',
 'Name': 'Warped Mind',
 'Persistent ID': 'BB925F8B0C12246C',
 'Play Count': '5',
 'Play Date': '3401878234',
 'Play Date UTC': '2011-10-19T20:10:34Z',
 'Sample Rate': '44100',
 'Size': '17639662',
 'Skip Count': '1',
 'Skip Date': '2009-12-23T20:32:51Z',
 'Total Time': '432875',
 'Track ID': '4138',
 'Track Type': 'File',
 'Year': '2008'}
 """

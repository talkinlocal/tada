from yapsy.IPlugin import IPlugin
import jinja2
import gzip
from lxml.etree import tostring,CDATA
from lxml.builder import E
from os import listdir,error,path

class IPBBackend(IPlugin):
    pack = None
    icondef = ""
        
    def build(self, pack):
        self.xml = None
        self.pack = pack
        print "[IPB] Building xml archive..."
        self.buildxml()
        print "[IPB] Building gzip..."
        self.makeGZip()

    def buildxml(self):
        import time
        import base64
        timestamp = int(time.time())
        fileset = E.fileset()
        emogroup = E.emogroup()
        for emote in self.pack.emotelist:
            with open(path.join("input", emote.filename), "rb") as image:
                encoded_image = base64.b64encode(image.read())
            fileset.append(
                   E.file(
                        E.filename(emote.filename),
                        E.content(encoded_image),
                        E.path("./style_emoticons/TADA"),
                        E.binary("1")
                       )
                   )
            for shortcut in emote.shortcuts:
                typed = E.typed()
                typed.text = CDATA(shortcut)
                emogroup.append(
                        E.emoticon(
                            typed, 
                            E.image(
                                emote.filename
                            ),
                            E.clickable(
                                "0"
                            ),
                        ))

        emoticonexport = E.emoticonexport(emogroup)
        emoticonexport.set("created", str(timestamp))
        emoticonexport.set("name", "TADA-generated")

        emoxml = tostring(emoticonexport, pretty_print=False, xml_declaration=False, encoding='UTF-8')

        fileset.append( E.file(
                            E.filename("emoticon_data.xml"),
                            E.content(base64.b64encode(emoxml)),
                            E.path(""),
                            E.binary("0")
                            )
                        )
       
        xmlarchive = E.xmlarchive(fileset)
        xmlarchive.set("created", str(timestamp))
        xmlarchive.set("generator", "TADA")

        self.xml = tostring(xmlarchive, pretty_print=False, xml_declaration=True, encoding='UTF-8')

    def makeGZip(self):
        try:
            fd = gzip.GzipFile(filename=path.join("output","ipb_emoticons.xml.gz"),
                    mode='wb',
                    compresslevel=9)
            fd.write(self.xml)
        except IOError as why:
            print "Failed to write xml file: ", e

    def buildicondef(self):
        env = jinja2.Environment(
            trim_blocks=True,
            lstrip_blocks=True
        )

        vacuumTemplate = env.from_string(self.template)
        self.icondef = vacuumTemplate.render(Emotes=self.pack)

    def makeZip(self):
        outzip = zipfile.ZipFile("output/psi.zip", 'w')
        outzip.writestr("BerachsEmotePack-psi/icondef.xml", self.icondef)
        for emote in self.pack.emotelist:
            try:
                outzip.write("input/"+emote.filename, "BerachsEmotePack-psi/"+emote.filename)
            except OSError:
                # The underlying emote file isn't found
                # This throws varying errors, but are all OSError or subclasses
                pass
        outzip.close()


    template = \
"""<?xml version='1.0' encoding='UTF-8'?>
<icondef>
    <meta>
        <name>{{ Emotes.name }}</name>
        <description> {{ Emotes.desc }} </description>
        <author>{{ Emotes.author }}</author>
        <version>{{ Emotes.version }}</version>
    </meta>

    {% for file in Emotes.emotelist %}
    <icon>
        {% for shortcut in file.shortcuts %}
        <text>{{ shortcut }}</text>
        {% endfor %}
        <object mime='{{ file.filetype }}'>{{ file.filename }}</object>
    </icon>

    {% endfor %}
</icondef>"""

from yapsy.IPlugin import IPlugin
import jinja2
import gzip
from lxml.html import builder as E
from lxml.html import tostring

from os import listdir,error,path

class IPBBackend(IPlugin):
    pack = None
    icondef = ""
        
    def build(self, pack):
        self.html = None
        self.pack = pack
        print "[HTML] Building html..."
        self.buildhtml()

    def buildhtml(self):
        import time
        import base64
        timestamp = int(time.time())
        page = E.HTML()
        page.append(E.HEAD(E.TITLE("OI Smileys")))
        body = E.BODY()
        table = E.TABLE()

        for emote in self.pack.emotelist:
            for shortcut in emote.shortcuts:
                table.append(
                        E.TR(
                            E.TD(
                                shortcut
                                ),
                            E.TD(
                                E.IMG(src=emote.filename),
                                ),
                        ),
                    )

        body.append(table)
        page.append(body)
        self.html = tostring(page, pretty_print=False,)

        open(path.join("output", "index.html"), "wb").write(self.html)


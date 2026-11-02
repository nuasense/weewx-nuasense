# Installer for the NuaSense uploader.
#
#   weectl extension install weewx-nuasense.zip      (weewx 5)
#   wee_extension --install weewx-nuasense.zip       (weewx 4)
#
# Adds [StdRESTful][[NuaSense]] to weewx.conf and registers the service. Put
# the token from the NuaSense console into `token`, restart weewx, done.

from weecfg.extension import ExtensionInstaller

VERSION = "0.1.0"
DEFAULT_URL = "http://ingest.nuasense.com/weatherstation/updateweatherstation.php"


def loader():
    return NuaSenseInstaller()


class NuaSenseInstaller(ExtensionInstaller):
    def __init__(self):
        super().__init__(
            version=VERSION,
            name="nuasense",
            description="Upload each archive record to NuaSense: your station, with the agronomy computed on it.",
            author="NuaSense",
            author_email="manuel@nuasense.com",
            restful_services="user.nuasense.NuaSense",
            config={
                "StdRESTful": {
                    "NuaSense": {
                        "enable": "true",
                        # The part after /station/ in the path the NuaSense
                        # console shows under External stations → Add a station.
                        "token": "replace_me",
                        "station": "weewx",
                        "server_url": DEFAULT_URL,
                    }
                }
            },
            files=[("bin/user", ["bin/user/nuasense.py"])],
        )

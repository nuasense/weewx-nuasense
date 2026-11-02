"""NuaSense uploader for weewx.

Posts every archive record to NuaSense in the Wunderground format, which is
what the NuaSense station receiver speaks (alongside Ecowitt and Ambient). The
heavy lifting — the queue, the retries, the record augmentation, the URL —
is weewx's own AmbientThread; this file only points it at NuaSense and gives
it the station's token as the Wunderground "password".

weewx.conf:

    [StdRESTful]
        [[NuaSense]]
            enable = true
            token = kw7n-4hpd-x2vt      # from the NuaSense console
            station = weewx             # any text; it just cannot be empty
            server_url = http://ingest.nuasense.com/weatherstation/updateweatherstation.php

Your data: NuaSense stores the readings and computes your forecast, spray
windows and risks from them; uses them aggregated and anonymised to improve
forecasts and models for everyone; never passes them on individually without
your opt-in. Disconnect the station in the console at any time and have its
data deleted.
"""

import logging
import queue

import weewx
import weewx.manager
from weewx.restx import AmbientThread, StdRESTful, get_site_dict

log = logging.getLogger(__name__)

VERSION = "0.1.0"
DEFAULT_URL = "http://ingest.nuasense.com/weatherstation/updateweatherstation.php"
PROTOCOL_NAME = "NuaSense"


class NuaSense(StdRESTful):
    """Archive records → NuaSense, one post per record."""

    def __init__(self, engine, config_dict):
        super().__init__(engine, config_dict)

        site = get_site_dict(config_dict, "NuaSense", "token")
        if site is None:
            return

        token = str(site.pop("token", "")).strip()
        if not token or token.lower().startswith("replace"):
            log.info("%s: no token in [StdRESTful][[NuaSense]]; nothing will be posted", PROTOCOL_NAME)
            return

        # Wunderground's two boxes: ID is any text, PASSWORD is what identifies
        # the station to NuaSense. The receiver reads the token from PASSWORD.
        site["station"] = str(site.pop("station", "weewx") or "weewx")
        site["password"] = token
        site.setdefault("server_url", DEFAULT_URL)
        site.pop("rapidfire", None)
        site.pop("archive_post", None)
        site.pop("rtfreq", None)

        manager_dict = weewx.manager.get_manager_dict_from_config(config_dict, "wx_binding")

        self.archive_queue = queue.Queue()
        self.archive_thread = AmbientThread(
            self.archive_queue,
            manager_dict,
            protocol_name=PROTOCOL_NAME,
            softwaretype="weewx-nuasense-%s" % VERSION,
            **site
        )
        self.archive_thread.start()
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        log.info("%s: data for station %s will be posted to %s", PROTOCOL_NAME, site["station"], site["server_url"])

    def new_archive_record(self, event):
        self.archive_queue.put(event.record)

from __future__ import annotations  # for union type
from urllib import parse as urlparse
from dataclasses import dataclass


@dataclass
class Result:
    parsed_url: urlparse.ParseResult

    @property
    def scheme(self) -> str:
        return self.parsed_url.scheme

    @property
    def url(self) -> str:
        return urlparse.urlunparse(self.parsed_url)

    @property
    def schemeless_url(self) -> str:
        u = self.url
        if self.scheme:
            u = u[len(self.scheme) + 1 :]
        if self.parsed_url.netloc:
            u = u.removeprefix("//")
        return u


def __canonical_host(host, respect_semantics):
    if not host:
        return ""

    host = host.lower()
    host = host.strip(".")

    if respect_semantics:
        return host

    for prefix in ["www.", "ww2.", "m.", "mobile."]:
        if host.startswith(prefix) and len(host) > (len(prefix) + 1):
            host = host[len(prefix) :]

    return host


def __canonical_path(scheme, path, respect_semantics):
    if not path:
        return ""

    if scheme in ["", "http", "https", "ftp", "file"]:
        absolute_path, segment = [], None
        for segment in path.split("/"):
            if segment == "":
                if not absolute_path:
                    absolute_path.append(segment)
            elif segment == ".":
                pass
            elif segment == "..":
                if len(absolute_path) > 1:
                    absolute_path.pop()
            else:
                absolute_path.append(segment)
        if segment in ["", ".", ".."]:
            absolute_path.append("")
        path = "/".join(absolute_path)

    if respect_semantics:
        return path

    suffixes = [
        "/default",
        "/index",
        ".htm",
        ".html",
        ".shtml",
        ".php",
        ".jsp",
        ".aspx",
        ".cms",
        ".md",
        ".pdf",
        ".stm",
        "/",
    ]
    found_suffix = True
    while found_suffix:
        found_suffix = False
        for suffix in suffixes:
            if path.endswith(suffix):
                path = path[: -len(suffix)]
                found_suffix = True

    return path


def __canonical_query(query, respect_semantics):
    pq = urlparse.parse_qsl(query, keep_blank_values=True)

    queries_to_skip = {
        # https://en.wikipedia.org/wiki/UTM_parameters
        "utm_term",
        "utm_campaign",
        "utm_content",
        "utm_source",
        "utm_medium",
        # https://en.wikipedia.org/wiki/Gclid
        "gclid",
        # https://en.wikipedia.org/wiki/Gclsrc
        "gclsrc",
        # https://en.wikipedia.org/wiki/Dclid
        "dclid",
        # https://en.wikipedia.org/wiki/Fbclid
        "fbclid",
    }

    if not respect_semantics:
        queries_to_skip |= {
            "cd-origin",
            "cmpid",
            "camp",
            "cid",
            "zanpid",
            "guccounter",
            "campaign_id",
            "tstart",
        }

    return sorted([q for q in pq if q[0] not in queries_to_skip])


def replace_last(s, old, new):
    h, _s, t = s.rpartition(old)
    return h + new + t


def __fragment_to_path(scheme, host, path, fragment):
    if not fragment:
        return None

    if scheme not in ("", "http", "https"):
        return None

    if host == "cnn.com" and path == "/video" and fragment.startswith("/"):
        return fragment

    if (
        host == "groups.google.com"
        and path.startswith("/forum")
        and fragment.startswith("!topic/")
    ):
        return "/g/" + fragment[len("!topic/") :].replace("/", "/c/", 1)

    if (
        host == "groups.google.com"
        and path.startswith("/forum")
        and fragment.startswith("!msg/")
    ):
        new_path = "/g/" + fragment[len("!msg/") :].replace("/", "/c/", 1)
        return replace_last(new_path, "/", "/m/")

    if path in ("", "/") and fragment.startswith("!"):
        new_path = fragment[1:]
        if not new_path.startswith("/"):
            new_path = "/" + new_path
        return new_path


def __canonical_webarchive(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host != "web.archive.org":
        return

    web_archive_prefix = "/web/"
    if not path.startswith(web_archive_prefix):
        return

    parts = path[len(web_archive_prefix) :].split("/", 1)
    if len(parts) == 2 and parts[1].startswith(("http:/", "https:/")):
        try:
            url = parts[1]
            url = url.replace("http:/", "http://", 1)
            url = url.replace("https:/", "https://", 1)
            u = cleanurl(
                url,
                generic=False,
                respect_semantics=respect_semantics,
                host_remap=host_remap,
            ).parsed_url
            return u.netloc, u.path, u.query
        except Exception:
            pass


def __canonical_youtube(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host in ("youtube.com", "www.youtube.com"):
        video_id = None
        if path == "/watch":
            for v in parsed_query or []:
                if v[0] == "v":
                    video_id = v[1]
                    break

        if path.startswith("/embed/"):
            path_parts = path.split("/")
            if len(path_parts) >= 3 and path_parts[-1] != "":
                video_id = path_parts[-1]

        if video_id:
            return "youtu.be", "/" + video_id, []

    if host_remap and host == "dev.tube" and path.startswith("/video/"):
        return "youtu.be", path[len("/video") :], []


def __canonical_medium(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host == "medium.com":
        path_parts = path.split("/")
        if len(path_parts) >= 3:
            return host, "/p/" + path_parts[-1].split("-")[-1], []
    if host.endswith(".medium.com"):
        path_parts = path.split("/")
        if len(path_parts) >= 2:
            return host, "/" + path_parts[-1].split("-")[-1], []


def __canonical_github(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host == "github.com":
        path = path.removesuffix("/tree/master")
        path = path.removesuffix("/blob/master/readme")

    return host, path, parsed_query


def __canonical_bitbucket(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host == "bitbucket.org":
        path = path.removesuffix("/src/master")

    return host, path, parsed_query


def __canonical_nytimes(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host == "nytimes.com":
        parsed_query = []
    if host == "open.nytimes.com":
        if path:
            parsed_query = []
            path_parts = path.split("/")
            if len(path_parts) >= 2:
                path = "/" + path_parts[-1].split("-")[-1]

    return host, path, parsed_query


def __canonical_techcrunch(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host == "techcrunch.com" or host.endswith(".techcrunch.com"):
        parsed_query = []

    return host, path, parsed_query


def __canonical_wikipedia(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host.endswith(".wikipedia.org"):
        for q in parsed_query:
            if q[0] == "title":
                path = "/wiki/" + q[1]
        parsed_query = []

    return host, path, parsed_query


def __canonical_arstechnica(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host == "arstechnica" and "viewtopic.php" not in path:
        parsed_query = []

    return host, path, parsed_query


def __canonical_bbc(host, path, parsed_query, respect_semantics, host_remap):
    if host_remap and (host == "bbc.co.uk" or host.endswith(".bbc.co.uk")):
        host = host.replace(".co.uk", ".com")

    if host in ("news.bbc.com", "news.bbc.co.uk"):
        parsed_query = []

    return host, path, parsed_query


def __canonical_twitter(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host in ("www.twitter.com", "twitter.com"):
        if path == "/home":
            path = ""
        else:
            path_parts = path.split("/")
            if (
                len(path_parts) == 4
                and path_parts[0] == ""
                and path_parts[2] == "status"
            ):
                path = "/i/status/" + path_parts[3]
                parsed_query = []

    if host_remap and host == "threadreaderapp.com":
        if path.startswith("/thread/"):
            path = "/i/status/" + path[len("/thread/") :]
            parsed_query = []
            host = "twitter.com"

    return host, path, parsed_query


def __canonical_specific_websites(
    host, path, parsed_query, respect_semantics, host_remap
):
    for h in [
        __canonical_webarchive,
        __canonical_youtube,
        __canonical_medium,
        __canonical_github,
        __canonical_bitbucket,
        __canonical_nytimes,
        __canonical_techcrunch,
        __canonical_wikipedia,
        __canonical_arstechnica,
        __canonical_bbc,
        __canonical_twitter,
    ]:
        result = h(host, path, parsed_query, respect_semantics, host_remap)
        if result:
            host, path, parsed_query = result
            host = host or ""
            path = path or ""
            parsed_query = parsed_query or []

    return host, path, parsed_query


__host_map = {"edition.cnn.com": "cnn.com"}


def _remap_host(host):
    return __host_map.get(host, host)


# todo: add note for schemeless urls


def cleanurl(
    url: str | urlparse.ParseResult,
    generic=False,
    respect_semantics=True,
    host_remap=True,
):
    if not url:
        return None

    u: urlparse.ParseResult

    if isinstance(url, str):
        try:
            u = urlparse.urlparse(url.strip())
        except Exception:
            return None
    else:
        u = url

    scheme = u.scheme
    host = __canonical_host(u.netloc, respect_semantics)
    path = __canonical_path(scheme, u.path, respect_semantics)
    parsed_query = __canonical_query(u.query, respect_semantics)
    fragment = u.fragment

    new_path = __fragment_to_path(scheme, host, path, fragment)
    if new_path is not None:
        path = new_path
        fragment = ""

    if not generic:
        host, path, parsed_query = __canonical_specific_websites(
            host, path, parsed_query, respect_semantics, host_remap
        )
        if host_remap:
            host = _remap_host(host)

    u = urlparse.ParseResult(
        scheme=scheme,
        netloc=host,
        path=path,
        params=u.params,
        query=urlparse.urlencode(parsed_query or []),
        fragment=fragment,
    )

    return Result(u)

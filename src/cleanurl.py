from __future__ import annotations  # for union type
from urllib import parse as urlparse
from dataclasses import dataclass
import re


def __replace_last(s, old, new):
    h, _s, t = s.rpartition(old)
    return h + new + t


def __is_integer(s):
    try:
        _ = int(s)
        return True
    except ValueError:
        return False


@dataclass
class Result:
    parsed_url: urlparse.ParseResult

    @property
    def scheme(self) -> str | None:
        return self.parsed_url.scheme

    @property
    def hostname(self) -> str | None:
        return self.parsed_url.hostname

    @property
    def netloc(self) -> str | None:
        return self.parsed_url.netloc

    @property
    def password(self) -> str | None:
        return self.parsed_url.password

    @property
    def port(self) -> int | None:
        return self.parsed_url.port

    @property
    def path(self) -> str | None:
        return self.parsed_url.path

    @property
    def query(self) -> str | None:
        return self.parsed_url.query

    @property
    def parsed_query(self) -> list[tuple[str, str]]:
        return urlparse.parse_qsl(
            self.parsed_url.query, keep_blank_values=True
        )

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
    host = re.sub(r"\.{2,}", ".", host)

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

    path = path.lower()

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
        and fragment.startswith("!forum/")
    ):
        return "/g/" + fragment[len("!forum/") :]

    if (
        host == "groups.google.com"
        and path.startswith("/forum")
        and fragment.startswith("!msg/")
    ):
        new_path = "/g/" + fragment[len("!msg/") :].replace("/", "/c/", 1)
        return __replace_last(new_path, "/", "/m/")

    if path in ("", "/") and fragment.startswith("!"):
        new_path = fragment[1:]
        if not new_path.startswith("/"):
            new_path = "/" + new_path
        return new_path


def __canonical_fragment(scheme, host, path, fragment, respect_semantics):
    if host in ("sbcl.org", "www.sbcl.org") and path in (
        "/news",
        "/news.html",
    ):
        return fragment

    if respect_semantics:
        return fragment
    else:
        return None


# fixme: the amped url may have a different scheme from the amp url
def __canonical_amp(host, path, parsed_query, respect_semantics, host_remap):
    path_is_amped_url = False
    if host in ("www.google.com", "google.com"):
        if path.startswith("/amp/"):
            path_is_amped_url = True

    # https://example-com.cdn.ampproject.org/c/s/example.com/g?value=Hello%20World

    if host.endswith(".cdn.ampproject.org"):
        path_is_amped_url = True

    if path_is_amped_url:
        parts = path.split("/")
        while parts and "." not in parts[0]:
            parts = parts[1:]

        path = "//" + "/".join(parts)
        if parsed_query:
            path += "?" + urlparse.urlencode(parsed_query)
        amped_url = cleanurl(
            path,
            respect_semantics=respect_semantics,
            host_remap=host_remap,
        )
        host = amped_url.parsed_url.netloc
        path = amped_url.parsed_url.path
        parsed_query = amped_url.parsed_query

    path = path.removeprefix("/amp/")

    return host, path, parsed_query


# fixme: the archived url may have a different scheme from the webarchive url
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
            )
            return u.parsed_url.netloc, u.parsed_url.path, u.parsed_query
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
            return "youtu.be", "/" + video_id.lower(), []

    if host_remap and host == "dev.tube" and path.startswith("/video/"):
        return "youtu.be", path[len("/video") :].lower(), []


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

        host_parts = host.split(".")
        if len(host_parts) == 4 and host_parts[1] == "m":
            host_parts.pop(1)

        if (
            not respect_semantics
            and len(host_parts) == 3
            and len(host_parts[0]) == 2
        ):
            host_parts.pop(0)

        host = ".".join(host_parts)

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

    if host in ("www.nitter.net", "nitter.net"):
        parts = path.split("/")
        if (
            len(parts) == 4
            and parts[0] == ""
            and parts[2] == "status"
            and __is_integer(parts[3])
        ):
            path = "/i/status/" + parts[3]
            parsed_query = []
            if host_remap:
                host = "twitter.com"

    queries_to_skip = {"src"}
    parsed_query = sorted(
        [q for q in parsed_query if q[0] not in queries_to_skip]
    )

    return host, path, parsed_query


def __canonical_mastodon(
    host, path, parsed_query, respect_semantics, host_remap
):
    parts = path.split("/")
    if (
        len(parts) == 4
        and parts[0] == ""
        and parts[1] == "web"
        and parts[2].startswith("@")
        and __is_integer(parts[3])
    ):
        parts.pop(1)
        path = "/".join(parts)
        parsed_query = []

    if host_remap:
        if (
            len(parts) == 3
            and parts[0] == ""
            and parts[1].startswith("@")
            and parts[1].count("@") == 2
            and "." in parts[1]
            and __is_integer(parts[2])
        ):
            account_parts = parts[1].split("@")
            if len(account_parts) == 3 and "." in account_parts[2]:
                host = account_parts[2]
                path = "@" + account_parts[1] + "/" + parts[2]
                parsed_query = []

    return host, path, parsed_query


def __canonical_reddit(
    host, path, parsed_query, respect_semantics, host_remap
):
    if host in ("reddit.com", "www.reddit.com", "old.reddit.com"):
        if host_remap:
            host = "reddit.com"
        else:
            if host != "old.reddit.com":
                host = "reddit.com"

    parts = path.split("/")
    if (
        len(parts) >= 5
        and parts[0] == ""
        and parts[1] == "r"
        and parts[3] == "comments"
    ):
        path = f"/{parts[1]}/{parts[2]}/{parts[3]}/{parts[4]}"
        parsed_query = []

    return host, path, parsed_query


def __canonical_stackoverflow(
    host, path, parsed_query, respect_semantics, host_remap
):
    parts = path.split("/")
    if (
        host.endswith(".com")
        and len(parts) == 4
        and parts[1] == "questions"
        and __is_integer(parts[2])
        and len(parts[3]) > 0
    ):
        path = "/q/" + parts[2]
        parsed_query = []

    return host, path, parsed_query


def __canonical_amazon(
    host, path, parsed_query, respect_semantics, host_remap
):
    host_parts = host.split(".")
    if len(host_parts) < 2:
        return
    if host_parts[0] == "www":
        host_parts = host_parts[1:]

    if host_parts[0] == "amazon":
        parts = path.split("/")
        parts = [p for p in parts if p]
        for i, p in enumerate(parts):
            if p == "dp" and i + 1 < len(parts):
                path = f"/{parts[i]}/{parts[i+1]}"
                parsed_query = []
                break

        if host_remap:
            host = ".".join(host_parts)

    return host, path, parsed_query


def __canonical_tumblr(
    host, path, parsed_query, respect_semantics, host_remap
):
    if not host:
        return

    host_parts = host.split(".")
    if not (
        len(host_parts) >= 3
        and host_parts[-2] == "tumblr"
        and host_parts[-1] == "com"
    ):
        return

    path_parts = path.split("/")

    if (
        len(path_parts) >= 3
        and path_parts[1] == "post"
        and path_parts[2].isdigit()
    ):
        return host, "/post/" + path_parts[2], []


def __canonical_lwn(host, path, parsed_query, respect_semantics, host_remap):
    if host not in ("lwn.net", "www.lwn.net"):
        return

    path_parts = [p for p in path.split("/") if p]

    if (
        len(path_parts) >= 2
        and path_parts[0].lower() == "subscriberlink"
        and path_parts[1].isdigit()
    ):
        return host, "/Articles/" + path_parts[1], []


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
        __canonical_mastodon,
        __canonical_reddit,
        __canonical_stackoverflow,
        __canonical_amazon,
        __canonical_tumblr,
        __canonical_lwn,
    ]:
        result = None
        try:
            result = h(host, path, parsed_query, respect_semantics, host_remap)
        except Exception:
            pass
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
    respect_semantics=False,
    host_remap=True,
) -> Result | None:
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

    if u.scheme == "about" and u.path == "reader":
        pq = urlparse.parse_qs(u.query, keep_blank_values=True)
        urls = pq.get("url")
        if urls:
            return cleanurl(urls[0], generic, respect_semantics, host_remap)

    scheme = u.scheme

    host = __canonical_host(u.netloc, respect_semantics)
    path = __canonical_path(scheme, u.path, respect_semantics)
    parsed_query = __canonical_query(u.query, respect_semantics)
    fragment = u.fragment

    new_path = __fragment_to_path(scheme, host, path, fragment)
    if new_path is not None:
        path = new_path
        fragment = ""

    fragment = (
        __canonical_fragment(scheme, host, path, fragment, respect_semantics)
        or ""
    )

    result = __canonical_amp(
        host, path, parsed_query, respect_semantics, host_remap
    )
    if result:
        host, path, parsed_query = result
        host = host or ""
        path = path or ""
        parsed_query = parsed_query or []

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

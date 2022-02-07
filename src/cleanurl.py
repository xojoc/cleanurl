from __future__ import annotations  # for union type
from urllib import parse as urlparse
import re
from dataclasses import dataclass


@dataclass
class Result:
    scheme: str
    schemeless_url: str
    parsed_url: urlparse.ParseResult

    @property
    def url(self) -> str:
        return f"{self.scheme}://{self.schemeless_url}"


def _canonical_host(host):
    if not host:
        return ''

    for prefix in ['www.', 'ww2.', 'm.', 'mobile.']:
        if host.startswith(prefix) and len(host) > (len(prefix) + 1):
            host = host[len(prefix):]

    return host


def _canonical_path(path):
    if not path:
        return ''

    path = re.sub('/+', '/', path)

    suffixes = [
        '/default', '/index', '.htm', '.html', '.shtml', '.php', '.jsp',
        '.aspx', '.cms', '.md', '.pdf', '.stm', '/'
    ]
    found_suffix = True
    while found_suffix:
        found_suffix = False
        for suffix in suffixes:
            if path.endswith(suffix):
                path = path[:-len(suffix)]
                found_suffix = True

    return path


def _canonical_query(query):
    pq = urlparse.parse_qsl(query, keep_blank_values=True)

    queries_to_skip = {
        'cd-origin',
        'utm_term', 'utm_campaign', 'utm_content', 'utm_source', 'utm_medium',
        'cmpid', 'camp', 'cid',
        'gclid', 'gclsrc', 'dclid', 'fbclid', 'zanpid',
        'guccounter', 'campaign_id', 'tstart'
    }

    return sorted([q for q in pq if q[0] not in queries_to_skip])


def replace_last(s, old, new):
    h, _s, t = s.rpartition(old)
    return h + new + t


def _fragment_to_path(host, path, fragment):
    if not fragment:
        return None

    new_path = None

    if (path == '' and fragment.startswith('!')):

        new_path = fragment[1:]
        if not new_path.startswith('/'):
            new_path = '/' + new_path

    if (host == 'cnn.com' and path == '/video' and fragment.startswith('/')):
        new_path = fragment

    if (host == 'groups.google.com' and path.startswith('/forum')
            and fragment.startswith('!topic/')):
        new_path = "/g/" + fragment[len('!topic/'):].replace("/", "/c/", 1)

    if (host == 'groups.google.com' and path.startswith('/forum')
            and fragment.startswith('!msg/')):
        new_path = "/g/" + fragment[len('!msg/'):].replace("/", "/c/", 1)
        new_path = replace_last(new_path, "/", "/m/")

    return new_path


def _canonical_webarchive(host, path, parsed_query):
    web_archive_prefix = '/web/'
    if host == 'web.archive.org':
        if path:
            if path.startswith(web_archive_prefix):
                parts = path[len(web_archive_prefix):].split('/', 1)
                if len(parts) == 2 and \
                   parts[1].startswith(('http:/', 'https:/')):
                    try:
                        url = parts[1]
                        url = url.replace("http:/", "http://", 1)
                        url = url.replace("https:/", "https://", 1)
                        u = cleanurl(url).parsed_url
                        host = u.netloc
                        path = u.path
                        parsed_query = u.query
                    except Exception:
                        pass

    return host, path, parsed_query


def _canonical_youtube(host, path, parsed_query):
    if host == 'youtube.com':
        if path:
            if path == '/watch':
                for v in (parsed_query or []):
                    if v[0] == 'v':
                        host = 'youtu.be'
                        path = '/' + v[1]
                        parsed_query = []
                        break

            if path.startswith("/embed/"):
                path_parts = path.split('/')
                if len(path_parts) >= 3 and path_parts[-1] != '':
                    host = 'youtu.be'
                    path = '/' + path_parts[-1]
                    parsed_query = None

    if host == 'dev.tube' and path and path.startswith('/video/'):
        path = path[len('/video'):]
        host = 'youtu.be'
        parsed_query = []

    return host, path, parsed_query


def _canonical_medium(host, path, parsed_query):
    if host == 'medium.com':
        if path:
            path_parts = path.split('/')
            if len(path_parts) >= 3:
                path = '/p/' + path_parts[-1].split('-')[-1]
    if host.endswith('.medium.com'):
        if path:
            path_parts = path.split('/')
            if len(path_parts) >= 2:
                path = '/' + path_parts[-1].split('-')[-1]

    return host, path, parsed_query


def _canonical_github(host, path, parsed_query):
    if host == 'github.com':
        if path:
            path = path.removesuffix('/tree/master')
            path = path.removesuffix('/blob/master/readme')

    return host, path, parsed_query


def _canonical_bitbucket(host, path, parsed_query):
    if host == 'bitbucket.org':
        if path:
            path = path.removesuffix('/src/master')

    return host, path, parsed_query


def _canonical_nytimes(host, path, parsed_query):
    if host == 'nytimes.com':
        parsed_query = []
    if host == 'open.nytimes.com':
        if path:
            parsed_query = []
            path_parts = path.split('/')
            if len(path_parts) >= 2:
                path = '/' + path_parts[-1].split('-')[-1]

    return host, path, parsed_query


def _canonical_techcrunch(host, path, parsed_query):
    if host == 'techcrunch.com' or host.endswith('.techcrunch.com'):
        parsed_query = []

    return host, path, parsed_query


def _canonical_wikipedia(host, path, parsed_query):
    if host.endswith('.wikipedia.org'):
        for q in parsed_query:
            if q[0] == 'title':
                path = '/wiki/' + q[1]
        parsed_query = []

    return host, path, parsed_query


def _canonical_arstechnica(host, path, parsed_query):
    if host == 'arstechnica' and 'viewtopic.php' not in path:
        parsed_query = []

    return host, path, parsed_query


def _canonical_bbc(host, path, parsed_query):
    if host and (host == 'bbc.co.uk' or host.endswith('.bbc.co.uk')):
        host = host.replace('.co.uk', '.com')

    if host == 'news.bbc.com':
        parsed_query = []

    return host, path, parsed_query


def _canonical_twitter(host, path, parsed_query):
    if not path:
        path = ''
    if host == 'twitter.com':
        if path == '/home':
            path = ''
        else:
            path_parts = path.split('/')
            if len(path_parts) == 4 and path_parts[0] == '' and path_parts[2] == 'status':
                path = "/i/status/" + path_parts[3]
                parsed_query = []

    if host == 'threadreaderapp.com':
        if path.startswith('/thread/'):
            path = '/i/status/' + path[len('/thread/'):]
            parsed_query = []
            host = 'twitter.com'

    return host, path, parsed_query


def _canonical_specific_websites(host, path, parsed_query):
    for h in [
            _canonical_webarchive, _canonical_youtube, _canonical_medium,
            _canonical_github, _canonical_bitbucket,
            _canonical_nytimes, _canonical_techcrunch,
            _canonical_wikipedia, _canonical_arstechnica, _canonical_bbc,
            _canonical_twitter
    ]:
        host, path, parsed_query = h(host, path, parsed_query)
    return host, path, parsed_query


__host_map = {'edition.cnn.com': 'cnn.com'}


def _remap_host(host):
    return __host_map.get(host) or host

# todo: host remap flag (dev.tube, threadapp, etc.)


def cleanurl(url: str | urlparse.ParseResult,
             generic=False,
             respect_semantics=True):

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

    host = _canonical_host(u.netloc)
    path = _canonical_path(u.path)
    parsed_query = _canonical_query(u.query)
    fragment = u.fragment

    new_path = _fragment_to_path(host, path, fragment)
    if new_path is not None:
        path = new_path
        fragment = ""

    if not generic:
        host, path, parsed_query = _canonical_specific_websites(
            host, path, parsed_query)

    host = _remap_host(host)

    query = urlparse.urlencode(parsed_query or [])

    path = path or ''

    schemeless_url = f"{host}{path}"

    if query:
        schemeless_url += f"?{query}"

    if fragment:
        schemeless_url += f"#{fragment}"

    u = urlparse.ParseResult(scheme=u.scheme or 'htt',
                             netloc=host,
                             path=path,
                             params=u.params,
                             query=query,
                             fragment=fragment)

    r = Result(u.scheme, schemeless_url, u)

    return r

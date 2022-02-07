import cleanurl
import unittest


class Clean(unittest.TestCase):
    def test_semantics(self):
        urls = ['https://www.xojoc.pw/blog/////focus.html',
                'xojoc.pw/blog/focus.html']

        return

        for u, r in zip(urls[0::2], urls[1::2]):
            c = cleanurl.cleanurl(u, generic=False, respect_semantics=True)
            self.assertEqual(c.schemeless_url, r)

    def test_no_semantics(self):
        urls = ["https://medium.com/swlh/caching-and-scaling-django-dc80a54012",
                "medium.com/p/dc80a54012",
                "https://bgolus.medium.com/the-quest-for-very-wide-outlines-ba82ed442cd9",
                "bgolus.medium.com/ba82ed442cd9",
                "http://www.path-normalization.com/a///index.html////",
                "path-normalization.com/a",
                "https://www.youtube.com/watch?v=71SsVUmT1ys&ignore=query",
                "youtu.be/71SsVUmT1ys",
                "https://www.youtube.com/embed/71SsVUmT1ys?ignore=query",
                "youtu.be/71SsVUmT1ys",
                "https://www.xojoc.pw/blog/////focus.html",
                "xojoc.pw/blog/focus",
                "https://web.archive.org/web/20200103092739/https://www.xojoc.pw/blog/focus.html",
                "xojoc.pw/blog/focus",
                "https://twitter.com/#!wikileaks/status/1255304335887646721",
                "twitter.com/i/status/1255304335887646721",
                "https://threadreaderapp.com/thread/1453753924960219145",
                "twitter.com/i/status/1453753924960219145",
                "https://twitter.com/RustDiscussions/status/1448994137504686086",
                "twitter.com/i/status/1448994137504686086",
                "http://twitter.com/home",
                "twitter.com",
                "https://github.com/xojoc/discussions/tree/master",
                "github.com/xojoc/discussions",
                "https://github.com/satwikkansal/wtfpython/blob/master/readme.md",
                "github.com/satwikkansal/wtfpython",
                "https://groups.google.com/forum/#!topic/mozilla.dev.platform/1PHhxBxSehQ",
                "groups.google.com/g/mozilla.dev.platform/c/1PHhxBxSehQ",
                "https://groups.google.com/forum/?utm_term=0_62dc6ea1a0-4367aed1fd-246207570#!msg/mi.jobs/poxlcw8udk4/_ghzqb9sg9gj",
                "groups.google.com/g/mi.jobs/c/poxlcw8udk4/m/_ghzqb9sg9gj",
                "https://www.nytimes.com/2006/10/11/technology/11yahoo.html?ex=1318219200&en=538f73d9faa9d263&ei=5090&partner=rssuserland&emc=rss",
                "nytimes.com/2006/10/11/technology/11yahoo",
                "https://open.nytimes.com/tracking-covid-19-from-hundreds-of-sources-one-extracted-record-at-a-time-dd8cbd31f9b4",
                "open.nytimes.com/dd8cbd31f9b4",
                "https://www.techcrunch.com/2009/05/30/vidoop-is-dead-employees-getting-computers-in-lieu-of-wages/?awesm=tcrn.ch_2t3&utm_campaign=techcrunch&utm_content=techcrunch-autopost&utm_medium=tcrn.ch-twitter&utm_source=direct-tcrn.ch",
                "techcrunch.com/2009/05/30/vidoop-is-dead-employees-getting-computers-in-lieu-of-wages",
                "https://dev.tube/video/EZ05e7EMOLM",
                "youtu.be/EZ05e7EMOLM",
                "https://edition.cnn.com/2021/09/29/business/supply-chain-workers/index.html",
                "cnn.com/2021/09/29/business/supply-chain-workers"]

        for u, r in zip(urls[0::2], urls[1::2]):
            c = cleanurl.cleanurl(u,
                                  generic=False,
                                  respect_semantics=False)
            self.assertEqual(c.schemeless_url, r)

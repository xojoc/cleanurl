import cleanurl
import unittest


class Clean(unittest.TestCase):
    def test_result(self):
        r = cleanurl.cleanurl("hTTps://gnu.org")
        self.assertEqual(r.scheme, "https")
        self.assertEqual(r.url, "https://gnu.org")
        self.assertEqual(r.schemeless_url, "gnu.org")

        r = cleanurl.cleanurl("//gnu.org")
        self.assertEqual(r.scheme, "")
        self.assertEqual(r.url, "//gnu.org")
        self.assertEqual(r.schemeless_url, "gnu.org")

        r = cleanurl.cleanurl("gnu.org")
        self.assertEqual(r.scheme, "")
        self.assertEqual(r.parsed_url.netloc, "")
        self.assertEqual(r.parsed_url.path, "gnu.org")
        self.assertEqual(r.url, "gnu.org")
        self.assertEqual(r.schemeless_url, "gnu.org")

    def test_semantics(self):
        urls = [
            "hTTps://www...xOjoC.pw./blog",
            "www.xojoc.pw/blog",
            "https://www.xojoc.pw/blog/////focus.html",
            "www.xojoc.pw/blog/focus.html",
            "https://www.xojoc.pw//.././///b/../a.html",
            "www.xojoc.pw/a.html",
            "https://www.xojoc.pw/blog/focus.html?utm_content=buffercf3b2&utm_medium=social&utm_source=snapchat.com&utm_campaign=buffe",
            "www.xojoc.pw/blog/focus.html",
            "https://web.archive.org/web/20200103092739/https://www.xojoc.pw/blog/focus.html",
            "www.xojoc.pw/blog/focus.html",
            "https://www.twitter.com/#!wikileaks/status/1255304335887646721",
            "www.twitter.com/i/status/1255304335887646721",
            "https://www.google.com/amp/www.example.com/amp/doc.html",
            "www.example.com/doc.html",
            "https://example-com.cdn.ampproject.org/c/s/example.com/g?value=Hello%20World",
            "example.com/g?value=Hello+World",
            "https://example-com.cdn.ampproject.org/i/example.com/logo.png",
            "example.com/logo.png",
            "https://mastodon.social/web/@gitea@social.gitea.io/107576792277055419",
            "social.gitea.io/@gitea/107576792277055419",
            "https://mastodon.social/web/@compsci_discussions/107795852426456992",
            "mastodon.social/@compsci_discussions/107795852426456992",
            "https://nitter.net/AdamCSharp/status/1473035981511180291",
            "twitter.com/i/status/1473035981511180291",
            "https://twitter.com/hashtag/swiftui?src=hash",
            "twitter.com/hashtag/swiftui",
            "https://en.m.wikipedia.org/wiki/Daphne_Caruana_Galizia",
            "en.wikipedia.org/wiki/Daphne_Caruana_Galizia",
            "https://stackoverflow.com/questions/69503317/bubble-sort-slower-with-o3-than-o2-with-gcc",
            "stackoverflow.com/q/69503317",
            "https://aviation.stackexchange.com/questions/71119/would-converting-a-lazair-ultralight-to-4-x-3-hp-engines-and-using-the-props-as",
            "aviation.stackexchange.com/q/71119",
            "https://example.com/#keep-fragment",
            "example.com/#keep-fragment",
            "https://old.reddit.com/r/wallstreetbets/comments/sv6clr/there_wont_be_a_war_in_ukraine_because_russia/",
            "reddit.com/r/wallstreetbets/comments/sv6clr",
            "https://www.amazon.it/Free-Freedom-Paperback-Stallmans-Software-ebook/dp/B006GCNP5S/ref=sr_1_2?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=A32SDX7PEZAW&keywords=richard+stallman&qid=1645805689&sprefix=richard+stallman%2Caps%2C154&sr=8-2",
            "amazon.it/dp/B006GCNP5S",
            "https://amazon.com/dp/B006GCNP5S?keywords=richard+stallman",
            "amazon.com/dp/B006GCNP5S",
            "https://amazon.com/dp/B006GCNP5S",
            "amazon.com/dp/B006GCNP5S",
            "about:reader?url=https%3A%2F%2Fmedium.com%2Fstories-from-fawrakh%2Ftales-of-a-hybrid-generation-8ccc853cbb77",
            "medium.com/p/8ccc853cbb77",
            "https://lwn.net/SubscriberLink/909887/c69ee127309e50e3/",
            "lwn.net/Articles/909887",
            "https://lwn.net/SubscriberLink/909887/14eac5b0b6f59131/",
            "lwn.net/Articles/909887",
            "https://store.google.com/category/phones?hl=en-US",
            "store.google.com/category/phones",
            "https://store.google.com/category/phones?hl=not-lang",
            "store.google.com/category/phones?hl=not-lang",
            "https://dl.acm.org/doi/pdf/10.1145/3371071",
            "doi.org/10.1145/3371071",
            "https://dl.acm.org/doi/10.1145/3371071",
            "doi.org/10.1145/3371071",
            "https://www.tandfonline.com/doi/abs/10.1080/03085147.2019.1678262",
            "doi.org/10.1080/03085147.2019.1678262",
            "https://doi.org/10.1000/182",
            "doi.org/10.1000/182",
            "https://arxiv.org/pdf/2210.07230.pdf",
            "arxiv.org/abs/2210.07230",
            "https://thenewstack.io/rust-vs-go-why-theyre-better-together/?s=09",
            "thenewstack.io/rust-vs-go-why-theyre-better-together",
            "https://groups.google.com/forum/#!topic/mozilla.dev.platform/1PHhxBxSehQ",
            "groups.google.com/g/mozilla.dev.platform/c/1PHhxBxSehQ",
            "https://groups.google.com/forum/?utm_term=0_62dc6ea1a0-4367aed1fd-246207570#!msg/mi.jobs/poxlcw8udk4/_ghzqb9sg9gj",
            "groups.google.com/g/mi.jobs/c/poxlcw8udk4/m/_ghzqb9sg9gj",
            "https://groups.google.com/forum/#!forum/golang-nuts",
            "groups.google.com/g/golang-nuts",
            "https://www.typescriptlang.org/play#code/JYOwLgpgTgZghgYwgAjMg3gWAFDL8uAIwQC4MBzMgZzClHIF8BuHfZAEwhjPXbJACuAW0LRmOBjhwIA9iBrJuyAApwoYYHAA2AHjAA+ZAF4MrfEVIUyAcgAW1hgBozeTkt5kA7JOzjs0uQU4Y2RrC2sCKmQAawgATxkYVBZ-bFl5NCgQmABtOABdFNyCkKgmIA",
            "www.typescriptlang.org/play?code=JYOwLgpgTgZghgYwgAjMg3gWAFDL8uAIwQC4MBzMgZzClHIF8BuHfZAEwhjPXbJACuAW0LRmOBjhwIA9iBrJuyAApwoYYHAA2AHjAA%2BZAF4MrfEVIUyAcgAW1hgBozeTkt5kA7JOzjs0uQU4Y2RrC2sCKmQAawgATxkYVBZ-bFl5NCgQmABtOABdFNyCkKgmIA",
        ]

        for u, r in zip(urls[0::2], urls[1::2]):
            c = cleanurl.cleanurl(u, generic=False, respect_semantics=True)
            self.assertEqual(c.schemeless_url, r, msg=u)

            self.assertEqual(
                c.schemeless_url,
                cleanurl.cleanurl(
                    c.url, generic=False, respect_semantics=True
                ).schemeless_url,
                msg=f"Clean clean {c.schemeless_url}",
            )

    def test_semantics_no_host_remap(self):
        urls = [
            "https://mastodon.social/web/@gitea@social.gitea.io/107576792277055419",
            "mastodon.social/@gitea@social.gitea.io/107576792277055419",
            "https://nitter.net/AdamCSharp/status/1473035981511180291",
            "nitter.net/i/status/1473035981511180291",
            "https://bgolus.medium.com/the-quest-for-very-wide-outlines-ba82ed442cd9",
            "bgolus.medium.com/ba82ed442cd9",
        ]

        for u, r in zip(urls[0::2], urls[1::2]):
            c = cleanurl.cleanurl(
                u, generic=False, respect_semantics=True, host_remap=False
            )
            self.assertEqual(c.schemeless_url, r, msg=u)

            self.assertEqual(
                c.schemeless_url,
                cleanurl.cleanurl(
                    c.url,
                    generic=False,
                    respect_semantics=True,
                    host_remap=False,
                ).schemeless_url,
                msg=f"Clean clean {c.schemeless_url}",
            )

    def test_no_semantics(self):
        urls = [
            "https://medium.com/swlh/caching-and-scaling-django-dc80a54012",
            "medium.com/p/dc80a54012",
            "https://bgolus.medium.com/the-quest-for-very-wide-outlines-ba82ed442cd9",
            "medium.com/p/ba82ed442cd9",
            "http://www.path-normalization.com/a///index.html////",
            "path-normalization.com/a",
            "https://www.youtube.com/watch?v=71SsVUmT1ys&ignore=query",
            "youtu.be/71ssvumt1ys",
            "https://www.xojoc.pw/blog/////focus.html",
            "xojoc.pw/blog/focus",
            "https://web.archive.org/web/20200103092739/https://www.xojoc.pw/blog/focus.html",
            "xojoc.pw/blog/focus",
            "https://twitter.com/#!wikileaks/status/1255304335887646721",
            "twitter.com/i/status/1255304335887646721",
            "https://threadreaderapp.com/thread/1453753924960219145",
            "twitter.com/i/status/1453753924960219145",
            "https://twitter.com/RustDiscussions/status/1448994137504686086?s=19",
            "twitter.com/i/status/1448994137504686086",
            "http://twitter.com/home",
            "twitter.com",
            "https://github.com/xojoc/discussions/tree/master",
            "github.com/xojoc/discussions",
            "https://github.com/satwikkansal/wtfpython/blob/master/readme.md",
            "github.com/satwikkansal/wtfpython",
            "https://www.nytimes.com/2006/10/11/technology/11yahoo.html?ex=1318219200&en=538f73d9faa9d263&ei=5090&partner=rssuserland&emc=rss",
            "nytimes.com/2006/10/11/technology/11yahoo",
            "https://open.nytimes.com/tracking-covid-19-from-hundreds-of-sources-one-extracted-record-at-a-time-dd8cbd31f9b4",
            "open.nytimes.com/dd8cbd31f9b4",
            "https://www.techcrunch.com/2009/05/30/vidoop-is-dead-employees-getting-computers-in-lieu-of-wages/?awesm=tcrn.ch_2t3&utm_campaign=techcrunch&utm_content=techcrunch-autopost&utm_medium=tcrn.ch-twitter&utm_source=direct-tcrn.ch",
            "techcrunch.com/2009/05/30/vidoop-is-dead-employees-getting-computers-in-lieu-of-wages",
            "https://dev.tube/video/EZ05e7EMOLM",
            "youtu.be/ez05e7emolm",
            "https://www.youtube.com/embed/71SsVUmT1ys?ignore=query",
            "youtu.be/71ssvumt1ys",
            "https://edition.cnn.com/2021/09/29/business/supply-chain-workers/index.html",
            "cnn.com/2021/09/29/business/supply-chain-workers",
            "https://www.google.com/amp/s/www.cnbc.com/amp/2021/04/27/archegos-hit-to-ubs-stuns-investors-as-shares-slide.html",
            "cnbc.com/2021/04/27/archegos-hit-to-ubs-stuns-investors-as-shares-slide",
            "https://en.m.wikipedia.org/wiki/Daphne_Caruana_Galizia",
            "wikipedia.org/wiki/daphne_caruana_galizia",
            "https://example.com/#remove-fragment",
            "example.com",
            "https://demo.tumblr.com/post/232/an-example-post",
            "demo.tumblr.com/post/232",
            "https://xojoc.pw/path#remove-fragment",
            "xojoc.pw/path",
            "http://www.sbcl.org/news.html#2.2.5",
            "sbcl.org/news#2.2.5",
            "https://www.cloudflare.com/it-it/learning/security/glossary/what-is-bgp/",
            "cloudflare.com/learning/security/glossary/what-is-bgp",
            "https://www.typescriptlang.org/play?#code/Base64",
            "typescriptlang.org/play?code=Base64",
            "https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/",
            "docs.djangoproject.com/howto/deployment/asgi",
        ]

        for u, r in zip(urls[0::2], urls[1::2]):
            c = cleanurl.cleanurl(u, generic=False, respect_semantics=False)
            self.assertEqual(c.schemeless_url, r)

            self.assertEqual(
                c.schemeless_url,
                cleanurl.cleanurl(
                    c.url, generic=False, respect_semantics=False
                ).schemeless_url,
                msg=f"Clean clean {c.schemeless_url}",
            )

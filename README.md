# cleanurl
Remove clutter from URLs and return a canonicalized version

# Install
```
pip install cleanurl
```
or if you're using poetry:
```
poetry add cleanurl
```

# Usage
By default *cleanurl* retuns a cleaned URL without respecting semantics.
For example:

```
>>> import cleanurl
>>> r = cleanurl.cleanurl('https://www.xojoc.pw/blog/focus.html?utm_content=buffercf3b2&utm_medium=social&utm_source=snapchat.com&utm_campaign=buffe')
>>> r.url
'https://xojoc.pw/blog/focus'
>>> r.parsed_url
ParseResult(scheme='https', netloc='xojoc.pw', path='/blog/focus', params='', query='', fragment='')
```

The default parameters are useful if you want to get a *canonical* URL without caring if the resulting URL is still valid.

If you want to get a clean URL which is still valid call it like this:

```
>>> r = cleanurl.cleanurl('https://www.xojoc.pw/blog/////focus.html', respect_semantics=True)
>>> r.url
'https://www.xojoc.pw/blog/focus.html'
```

```celeanurl.cleanurl``` parameters:

 - ```generic``` -> if True don't use site specific rules
 - ```respect_semantics``` -> if True make sure the returned URL is still valid, altough it may still contain some superfluous elements
 - ```host_remap``` -> whether to remap hosts. Example:
```
>>> import cleanurl
>>> cleanurl.cleanurl('https://threadreaderapp.com/thread/1453753924960219145', host_remap=True).url
'https://twitter.com/i/status/1453753924960219145'
>>> cleanurl.cleanurl('https://threadreaderapp.com/thread/1453753924960219145', host_remap=False).url
'https://threadreaderapp.com/thread/1453753924960219145'
```

For more examples see the [unit tests](https://github.com/xojoc/cleanurl/blob/main/src/test_cleanurl.py).


# Why?
While there are some libraries that handle general cases, this library has website specific rules that more aggresivly normalize urls.

# Users
Initially used for [discu.eu](https://discu.eu).

[Discussions around the web](https://discu.eu/q/https://github.com/xojoc/cleanurl)

# Who?
*cleanurl* was written by [Alexandru Cojocaru](https://xojoc.pw).

# License
*cleanurl* is [Free Software](https://www.gnu.org/philosophy/free-sw.html) and is released as [AGPLv3](https://github.com/xojoc/cleanurl/blob/main/LICENSE)
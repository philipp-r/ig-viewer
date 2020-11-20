# IG Viewer

Build with Python.

## Running

1. Get "Export Cookies" Addon for Firefox <https://addons.mozilla.org/de/firefox/addon/export-cookies/>

2. Login to instagram.com with Firefox browser

3. Export cookies in *cookies.txt* file

4. Create *users.json* file with the users you want to follow:

```
    {
    	"follow": [
    		"USERNAME_ONE",
    		"USERNAME_TWO",
    		"SOME_OTHER_USER",
    		"LAST_USER"
    	]
    }
```

5. Run `python get.py`
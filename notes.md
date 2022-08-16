## In progress
- added task feature
- but now everything is a real mess
- think about how to refactor everything to be DRY-er
    - maybe macros? use more python logic and less template logic?
    - classes for template display/template objects

## For later
- refactor tests to work with updates
    - save for final refacor, lots to fix already
- rework CSS for better layout/asthetics
- database schema modifications
    - add a temp_schema file?
    - migrate logic in db.py file??
- make detail view show print layout styling?
- add some fun to landing page?
- sort/search functionality??
- sort tasks by due date?

## Code snippets
MathJax config:

```
<script type="text/x-mathjax-config">
    MathJax.Hub.Config({
      config: ["MMLorHTML.js"],
      jax: ["input/TeX", "output/HTML-CSS", "output/NativeMML"],
      extensions: ["MathMenu.js", "MathZoom.js"]
    });
    </script>
``` 

SQL Console
```
import sqlite3
conn = sqlite3.connect('instance/noter.sqlite')
cur = conn.cursor()

cur.execute("""
SQL statements...
""")

#use fetchone() fetchall() to get results
```

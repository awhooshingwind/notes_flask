## In progress
- refactoring views
    - detail view will show secret notes (check for auth) **FIXED**
- private index vs public **WORKING**
    - sorting working in index template, but could be better
    - refactoring view code with this is mind
- show private notes but hide note body?? **WORKING**
    - current (unintentional) behavior of index template

## For later
- add functionality for footer??
- refactor tests to work with updates
    - save for final refacor, or build in working index private behavior?
- rework CSS for better layout/asthetics
- database schema modifications (ALTER table?)
    - add a temp_schema file?
- make detail view show print layout styling?
- add some fun python logic for landing page?
- sort/search functionality??

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
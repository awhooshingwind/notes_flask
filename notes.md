## In progress
- refactoring views
    - detail view will show secret notes (check for auth)
- private index vs public
    - sorting working in index template, but could be better
    - refactoring view code with this is mind
- show private notes but hide note body??
    - current (unintentional) behavior of index template

## For later
- refactor tests to work with updates
    - save for final refacor, or build in working index private behavior?
- rework CSS for better layout/asthetics

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
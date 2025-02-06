# Warsaw API Demo

aka. my slow descent into madness

## Running

### static (bundled) HTML file

just run the python script with:

```bash
python static.py
```

> to change start end stop points, edit the `static.py` file directly.


### server

```bash
bokeh serve --show server.py
```

(or you can ommit the `--show` flag, but you'll need to open the URL in your browser manually)

> to change start end stop points, edit the `server.py` file directly.


## Notes

- **nr zespołu** to numer kolekcji przystanków


## TODO

- [x] fix aspect ration - make 1:1
- [ ] improve performance
- [ ] allow selecting start and stop points
- [ ] fix html in the sidebar (fix issues and make controls section more standing out)
- [x] darw final path only on the last step

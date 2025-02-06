# Warsaw API Demo

aka. my slow descent into madness


## Installation

1. clone git repo

```bash
git clone https://github.com/pacjo/Procedural-POC
```

2. navigate to the `warsaw-demo` directory

```bash
cd src/warsaw-demo
```

3. install dependencies

- if you use [nixOS](https://nixos.org/), you can use the flake.nix file:

```bash
nix develop
```

- otherwise you'll need to install the dependencies manually (there's no requirements.txt file yet, so good luck)


## Running

For small files, you can get away with using the `static.py` script. For larger ones (and they can get quite large, I've seen 2.3GB once), you'll need to use the `server.py` script.


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


### headless for video creation


run the same as [`static`](#static-bundled-html-file), but use `frame_generator.py` instead of `static.py`. Resulting files will be saved in the `frames` directory and you can convert them into video later.


#### Converting resulting files into movies with ffmpeg

> For information on why does the command below work, see [this](https://stackoverflow.com/questions/24961127/how-to-create-a-video-from-images-with-ffmpeg).

1. navigate to the `frames` directory
2. run ffmpeg:

```bash
ffmpeg -framerate 30 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p out.mp4
```


## Notes

- **nr zespołu** to numer kolekcji przystanków


## TODO

- [x] fix aspect ration - make 1:1
- [ ] improve performance
- [ ] allow selecting start and stop points
- [ ] fix html in the sidebar (fix issues and make controls section more standing out)
- [x] darw final path only on the last step
- [ ] hide axis and title in `frame_generator.py`
- [ ] investigate weights and heuristic (maybe small numbers aren't meaningful enough?)
- [ ] update and better document ffmpeg commands

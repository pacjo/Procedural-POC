# Warsaw API Demo

aka. my slow descent into madness

![long-route](examples/long-route.gif)


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

For more information on rendering see [workflow for long "renders"](#workflow-for-long-renders) section.


#### Converting resulting files into movies with ffmpeg

> For information on why does the command below work, see [this](https://stackoverflow.com/questions/24961127/how-to-create-a-video-from-images-with-ffmpeg).


##### Realtime speed (most correct)

```bash
ffmpeg -framerate 30 -pattern_type glob -i 'frames/*.png' -c:v libx264 -pix_fmt yuv420p out.mp4
```


##### Speed up with time

With increasing number of nodes, the algorith will take longer to change meaningfully. We can speed up the video to make up for that.

```bash
ffmpeg -framerate 30 -pattern_type glob -i 'frames/*.png' -vf "setpts=0.5*PTS" -c:v libx264 -pix_fmt yuv420p out-speed.mp4
```


##### Conversion to GIFs

```bash
ffmpeg -i out.mp4 -loop 0 out.gif
```


## Notes

- **nr zespołu** to numer kolekcji przystanków


### Workflow for long renders

Doing long routes, due to bad code optimization and rather interesting method of doing screenshots by bokeh, requires significant amount of time. Script is singlethreaded, so this has to be worked around manually.

One option is to run multiple instances of `frame_generator.py` in parallel. You can select starting frame using the `Frame skipping block` found in the script.

Beware that not only is the script slow, it's also very memory intensive. Running 2-3 instances in parallel on a 16GB RAM machine is about the limit (you can try more if the path isn't that long).

With recent commits, script will no longer crash if there's an error during image capture, but image that caused the error, will be skipped. Make sure to check the logs and resulting files for missing images.


## TODO

- [x] fix aspect ration - make 1:1
- [ ] improve performance
- [ ] allow selecting start and stop points
- [ ] fix html in the sidebar (fix issues and make controls section more standing out)
- [x] darw final path only on the last step
- [ ] hide axis and title in `frame_generator.py`
- [ ] investigate weights and heuristic (maybe small numbers aren't meaningful enough?)
- [x] update and better document ffmpeg commands

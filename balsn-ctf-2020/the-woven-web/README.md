## Challenge Information

- Name: The Woven Web
- Type: Web
- Description:

```
BGM: [Animals as Leaders - The Woven Web](https://www.youtube.com/watch?v=g68hQ4zJ3t0)
```

- Files provided: `docker/`, but without the real FLAG in `docker/app/server.js`
- Solves: 6 / ???

## Build

```
docker-compose build
docker-compose up

# attach bash for debugging
docker ps
docker exec -it <CONTAINER ID> bash
```

## Writeup

Initially this challenge seems to be a XSS problem; there is a Selenium Chromium bot running in the backend. However the flag is in the file system `server.js`. What's worse, there is no chance to SSRF other services. Redis is listening on a Unix socket. The best we can to is to exploit `file:///` protocol and see if we can exfiltrate the flag out.

When running Chromium without headless mode enabled, it will download files to `Downloads/` in home directory. If the directory does not exist, Chromium will create it. Additionally, by default Chromium will download file automatically, even without user interaction. Therefore we can download arbitrary files to the server. In `exploit/server.php` we make the Chromium bot download `exp.html` to its home directory.

Next, Chromium has a strict same-origin policy on `file:///` protocols. `file:///home/user/app/server.js` and `file:///home/user/Downloads/exp.html` are considered different origins. We cannot just run `fetch()` and exfiltrate the content of `server.js`. However, because `server.js` is written in NodeJs, it's also a valid JavaScript file. We can exploit Cross-Site Script Inclusion (XSSI) to include this file. The browser will run `server.js` and set FLAG as a global variable. The rest is to exfiltrate the flag out. See `exploit/exp.html` for details.

### Unintended Solution

[Cyku](https://twitter.com/cyku_tw) exploits the Chromium using a XSS in node modules. 

> I solved the woven web by finding an eval javascript injection in /usr/share/npm/node_modules/columnify/node_modules/wcwidth/node_modules/defaults/node_modules/clone/test-apart-ctx.html

That is impressive! It means this challenge can be solved even with headless mode enabled. 

### Chromium 1-day

Because I use the Debian buster image, the version of Chromium is 83, which is a very old version. Some challengers told me that there is a lot of Chrome 1-day on version 83 in the wild. What's worse, I disabled sandbox feature because it's a common crawler settings. Fortunately, I didn't find any one exploit this challenge with 1-day. I guess Debian upstream applied some security patches even on old version of Chromium?

## Postscript

My research heavily relies on Chromium crawlers. One day I accidentally found there were a bunch of files under `~/Downloads`. I didn't even create the `Downloads` directory! Then, this feature inspired me to create a challenge.
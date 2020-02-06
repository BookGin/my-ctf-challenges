## Challenge Information

- Name: Imagination
- Type: Web
- Description:

```
In this challenge, each team will have an isolated environment (ssh proxy + web server),
which can be accessed via `ssh root@HOST -p $[60300+TEAM_ID]` with your team token as the password.
You can access the web server `http://imagination:8000` through the ssh proxy.
See ssh [local port forwarding](https://help.ubuntu.com/community/SSH/OpenSSH/PortForwarding#Local_Port_Forwarding) for help.

The flag is on the web server.

Disclaimer for fairness: this challenge MIGHT be related to [Images and Words](https://github.com/BookGin/my-ctf-challenges/tree/master/balsn-ctf-2019/images-and-words) in Balsn CTF 2019.
```

- Files provided: All the files under `build/imagination`, excluding the real flag
- Solves: 1 / 15

## Build

Each team will be given an ssh server and a web server. The password of ssh server is read from `enc_shadow`, which can be generated using this one-liner:

```
python3 -c 'import crypt,getpass; print(crypt.crypt(getpass.getpass(), crypt.mksalt(crypt.METHOD_SHA512)))'
```

Run the script to create environments for each teams:
```
./run.sh
```

## Writeup

In this challenge, We can read/write files in almost any subdirectory. Because it sanitizes `.`, we can't write files in the current working directory. Another tricky part is it will only create directory if the name is in that dictionary.

During Python execution, it will create a `__pycache__` directory in the current working directory. It will contain Python pre-compiled cache files. We can just send a request to `/__pycache__/server.cpython-38.pyc` to download it, though we already have the source code.

Remember that we can write files in subdirectory. The idea is pretty straightforward now --- overwrite the cache file to achieve RCE.

Just be careful when you try to overwrite the pyc file. You can refer to [this article](https://nedbatchelder.com/blog/200804/the_structure_of_pyc_files.html). Those magic strings as well as the modification timestamp should be left untouched. See `./exploit/exp.sh` for details.

The next step is to make the gunicorn server restart; otherwise the cache file will not be loaded. In this challenge, gunicorn is deployed without any proxy. That makes it [vulnerable to DoS attacks](https://docs.gunicorn.org/en/stable/deploy.html#nginx-configuration).

Also, gunicorn uses pre-forked worker processes with the [default timeout 30 seconds](https://docs.gunicorn.org/en/stable/settings.html#timeout). Actually, it's very easy to make gunicorn to restart the worker. Because it's configured without any proxy, simply creating a slow TCP connection will totally make the server freeze. See `./exploit/exp.sh` for details.

After it's timeout, gunicorn will restart the worker and load our crafted cache file. The full exploit is in `./exploit/exp.sh`.

```
[2020-02-06 07:44:09 +0000] [6] [CRITICAL] WORKER TIMEOUT (pid:220)
[2020-02-06 07:44:09 +0000] [220] [INFO] Worker exiting (pid: 220)
[2020-02-06 07:44:09 +0000] [221] [INFO] Booting worker with pid: 221
```

## Postscript

Deploying gunicorn without proxy like nginx is dangerous regarding performance. A slow TCP connection can DoS your server easily.
I just want to bring this up so I create this challenge.

The `__pycache__` part seems like a old trick. The design of writing to an exising subdirectory is kind of strange. There's definitely room for improvement.

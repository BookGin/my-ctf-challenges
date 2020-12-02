## Challenge Information

- Name: Windows XP Media Player
- Type: Misc, Web
- Description:

```
BGM: [Sunset Rollercoaster - Burgundy Red](https://www.youtube.com/watch?v=d1REzQ75COs)
```

- Files provided: `docker/`, but without the real FLAG in `docker/flag`
- Solves: 5 / ???

## Build

```
docker-compose build
docker-compose up

# attach bash for debugging
docker ps
docker exec -it <CONTAINER ID> bash
```

## Writeup

The challenge is pretty straight-forward. We can control the command line arguments under some limitations. The objective is to list the flag path and read the flag. There are many creative ways to solve this challenge. Here is the intended one:

- `shuf -e --output=/sandbox/UID/bar`: we can create more files in the working directory.

- `shuf -e --output=foo --zero-terminated /flag`: we can write a file path `/etc/hosts\x00` to a file `foo`
- `du --files0-from=foo --exclude=?flag?`: if the output is empty, that means the file under the path matches the glob expression.

Therefore, just enumerate the flag path and read the flag using `du --files0-from=/flag/bazz/123`. My incomplete solution is in `exploit/solve.py`

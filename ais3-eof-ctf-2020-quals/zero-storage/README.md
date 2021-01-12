## Challenge Information

- Name: Zero Storage
- Type: Web
- Description: 

```
1. There are two flags in this challenge. Flag A is in admin's uploaded file, and Flag B is admin's password. Note the two flags are independent. You can get either flag without the other one.
2. The source code is attached. Except for `zerostorage/app/server.py`, there is no intended vulnerability in this challenge, so basically just readling `server.py` is sufficient to get the two flags.
3. Enjoy the challenge!
```

- Files provided: `docker/`, but without `docker-compose.yaml`.
- Solves:
  - FLAG A (XSS): 47 / 55, (95 teams in total, but only 55 teams with scores > 1)
  - FLAG B (session): 41 / 55

## Build

```
docker-compose build
docker-compose up
```

## Writeup

TBD

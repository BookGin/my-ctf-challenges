## Challenge Information

- Name: Ponzi Scheme
- Type: Misc
- Description:

```
Just trust me and you'll make a fortune.
For PoW, you can use [these provided scripts](https://balsn.github.io/proof-of-work/).
Note: This is NOT a web challenge. There is no intended vulnerability in the web application.
```

- Files provided: None
- Solves: 51+ / 78+

## Build

```
docker-compose build
docker-compose up

# attach shell for debugging
docker ps
docker exec -it <CONTAINER ID> sh
```

## Writeup

As the name indicates, the idea is [Ponzi Scheme](https://en.wikipedia.org/wiki/Ponzi_scheme). 

### Intended Solution

1. Register 11 investors.
2. One of the investors invests on Plan C.
3. After 1795 seconds, the rest investors invest on any of the plans.
4. Profit and obtain the flag, unless other people get back a lot of money within the 6 seconds.

See `exploit/solve.py` for details.

### Unintended Solution

1. Register an investor.
2. Because Ponzi's balance is known, we can monitor it to infer other investors' plans.
3. For example, if the balance does not change in 6 seconds, it must be either Plan B or Plan C.
4. Profit by investing on a plan with a shorter term.

## Postscript

In the beginning, my idea was to make a challenge that challengers can play together. They can interact with each other,  instead of solving challenge alone. However, I had to be very careful that some challengers may prevent others from obtaining flags. At least minimizing this possibility is necessary.

In fact, one challenger created a number of investors with his tremendous computational resources. He actually had 200+ investors in the market. Although that might help other challengers solve this easily, that's how market works, right?

## Erratum and Caveats

1. Ponzi's highest balance is not properly updated during the challenge.
2. The Q&A's description is incorrect: it should be "... on plan (C), you can get back $10,000 after **1800 seconds**."
3. The [default SQLite lock timeout](https://docs.python.org/3.8/library/sqlite3.html#sqlite3.connect) in Python is 5 seconds, which is too short for large amount of traffic (people will bankrupt!). Consider increase the timeout or use other database. 

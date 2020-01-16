#!/usr/bin/env python3
from jinja2 import Template

debug = False
flag = 'FLAG{ponzi_scheme_fa_da_chai_$_$!!!}'

db_path = './db.sqlite3'
powser_path = './pow.sqlite3'
powser_diffculty = 22
powser_min_refresh_time = 540
powser_default_expired_time = 600

ponzi_uid = 'J2ASoCBy5HYIl8fdxq5janUPUybiSYmK'
ponzi_init_balance = 1000

user_init_balance = 1000

plans = {
    'names': ['(A) Coward', '(B) Fool', '(C) Entrepreneur'],
    'rate': ['2.33%', '25.90%', '900%'],
    'term': [6, 90, 1800],
    '_rate': [1.0233, 1.259, 10]
}

home_html = Template('''
<!DOCTYPE HTML>
<html>
<head>
    <title>Ponzi</title>
    <meta charset="utf-8" />
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <meta name="author" content="bookgin">

    <style type="text/css">
    body {
        background-color: #f0f0f2;
        margin: 0;
        padding: 0;
        font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    div {
        width: 900px;
        margin: 5em auto;
        padding: 50px;
        background-color: #fff;
        border-radius: 1em;
    }
    @media (max-width: 1000px) {
        body {
            background-color: #fff;
        }
        div {
            width: auto;
            margin: 0 auto;
            border-radius: 0;
            padding: 1em;
        }
    }
    </style>
</head>

<body>
<div>
    <p align="right">Your account balance: <b>$ {{user.balance}}</b></p>
    <img src="https://i.imgur.com/Mcep4IT.jpg" style="float:right;width:25%;"></img>
    <h1>This is Ponzi</h1>
    <p style="text-align:center;font-size:20px;">{{msg}}</p>
    <ul>
      {% for k, v in stats.items() %}
        <li>{{k}}: {{v}}</li>
      {% endfor %}
    </ul>
    <hr/>
    <h2>Choose your plan to invest Ponzi</h2>
    <table width="100%">
      <tr>
          <th>Plan</th>
          {% for i in plans['names']%}
            <th>{{i}}</th>
          {% endfor %}
      </tr>
      <tr>
          <td align="center">Term</td>
          {% for i in plans['term']%}
            <td align="center">{{i}} seconds</td>
          {% endfor %}
      </tr>
      <tr>
          <td align="center">Return</td>
          {% for i in plans['_rate']%}
            <td align="center">$ {{(user['balance'] * i)|int}}</td>
          {% endfor %}
      </tr>
      <tr>
          <td align="center">Return on Investment</td>
          {% for i in plans['rate']%}
            <td align="center">{{i}}</td>
          {% endfor %}
      </tr>
      <tr>
          <td align="center">Invest</td>
          {% for i in range(plans['names']|length) %}
            <td align="center">
              <form method="POST">
                <input type="text" name="plan" value="{{i}}" hidden><br/>
                <input type="text" name="csrf" value="{{user.csrf}}" hidden><br/>
                <input type="submit" value="Invest">
              </form>
            </td>
          {% endfor %}
      </tr>
    </table>
    <hr/>
    <h2>Q &amp; A</h2>
    <ol style="line-height:1.5;">
        <li>Q: What do those plans mean? <br>
        A: For instance, if you invest $1,000 on plan (C), you can get back $10,000 after 1800 seconds.</li>
        <li>Q: Is it required to invest all of my money? <br>
        A: Yes, it's all or nothing!</li>
        <li>Q: What if Ponzi doesn't have enough money to pay me? <br>
        A: Panzi will declare bankruptcy, and you will get nothing  ¯\_(ツ)_/¯.</li>
        <li>Q: How do I return to this page later? <br>
        A: Just add this page to My Favorites.</li>
    </ol>
</div>
</body>
</html>
''')

pow_html = Template('''
<!DOCTYPE HTML>
<html>
<head>
    <title>Ponzi</title>
    <meta charset="utf-8" />
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <meta name="author" content="bookgin">

    <style type="text/css">
    body {
        background-color: #f0f0f2;
        margin: 0;
        padding: 0;
        font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    div {
        width: 900px;
        margin: 5em auto;
        padding: 50px;
        background-color: #fff;
        border-radius: 1em;
    }
    @media (max-width: 1000px) {
        body {
            background-color: #fff;
        }
        div {
            width: auto;
            margin: 0 auto;
            border-radius: 0;
            padding: 1em;
        }
    }
    </style>
</head>

<body>
<div>
  <h1>Proof-of-Work</h1>
  <p>
    Computer an answer such that SHA256(<code>{{prefix}}</code> + answer) has {{difficulty}} leading zero bits:
  </p>
    <form>
      <p align="center">
      <input type="text" name="answer" placeholder="answer">
      <input type="submit" value="Submit">
      </p>
    </form>
  <hr/>
  <br>
  IP: {{ip}}<br>
  Time remain: {{time_remain}} seconds<br>
  You need to await {{time_remain - min_refresh_time}} seconds to get a new challenge.
</div>
</body>
</html>
''')

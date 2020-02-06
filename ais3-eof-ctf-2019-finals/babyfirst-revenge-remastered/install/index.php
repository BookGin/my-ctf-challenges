<?php
// Windows Server 2019 version 10.0.17763
highlight_file(__FILE__);
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
set_time_limit(10);
ini_set('max_execution_time', 10);

if (isset($_GET['cmd']) && strlen($_GET['cmd']) <= 7) {
  if (strlen($_GET['nonce']) < 8)
    die("invalid nonce");
  $sandbox = 'C:\\sandbox\\' . hash("sha256", "idea_from_orange_s_babyfirst_revenge" . $_GET['nonce']);
  @mkdir($sandbox);
  chdir($sandbox);
  system($_GET['cmd']);
} else {
  // helper: register a domain for you :)
  $domain = strval($_GET['domain']);
  $tld = strval($_GET['tld']);
  $ip = strval($_GET['ip']);

  if (!in_array($tld, ["tw", "tk", "ml", "ga", "cf", "gq", "co", "me", "xyz", "ninja", "solutions"]))
    die("invalid tld");

  if (!ctype_alnum($domain))
    die("invalid domain");
  if (strlen($domain) <= 3)
    die("the domain is too expensive");

  if (!filter_var($ip, FILTER_VALIDATE_IP))
    die("invalid ip address");
  $line = $ip . " " . $domain . "." . $tld;
  file_put_contents('C:\\windows\\system32\\drivers\\etc\\hosts', $line . PHP_EOL, FILE_APPEND | LOCK_EX);
  print($line);
}
?>

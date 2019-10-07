<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $file = $_FILES["file"];
    if ($file["size"] > 1000000)
        die("file too large");
    set_time_limit(15);
    ini_set('max_execution_time', 15);
    $name = "C:/upload/" . basename($_FILES["file"]["name"]);
    move_uploaded_file($file["tmp_name"], $name);
    system("python getsize.py ".escapeshellarg($name));
    unlink($name);
    die();
}
?>

<h2>What is this application?</h2>
<p>We use the latest machine learning technique "Revolutional Neural Network (RNN)"</br>
to help users get the size of images. You know, artificial intelligence is written</br>
in PowerPoint, but my machine learning is written in Python 3.7.4 and imageio 2.5.0.</p>

<h2>Which operation system do you use?</h2>
<p> Windows Server 2019 version 10.0.17763.0, and this OS is designed by the company who owns GitHub.</p>

<h2>What kind of image format do you support?</h2>
<p>Here is <a href="https://imageio.readthedocs.io/en/v2.5.0/formats.html#single-images">the list</a> of support image formats. Some require external libraries or programs.</br>
I think I installed all of them. If you find some library or program is missing, please let me know.</p>

<h2>Is pwn/binary exploit skill required to solve this?</h2>
<p>No.</p>

<h2>I found Ghostscript is missing. Could you install it?</h2>
<p>No.</p>

<form action="/" method="POST" enctype="multipart/form-data">
    Select image to upload:
    <input type="file" name="file">
    <input type="submit" value="Upload" name="submit">
</form>

<?php
highlight_file(__FILE__);
highlight_file("getsize.py");
?>

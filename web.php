<!DOCTYPE HTML>
<html>
<head>
	<title>IG Viewer</title>
</head>
<body>
<?php
if ($handle = opendir('.')) {
    while (false !== ($entry = readdir($handle))) {
        if (strpos($entry, 'recent-') !== false) {
        	$img_data = explode("-", $entry);
        	echo '@'.$img_data[2].'  '.date("d.m.Y H:i",$img_data[1]).'<br>';
            echo '<img src="'.$entry.'">';
            echo '<hr>';
        }
    }
    closedir($handle);
}

?>
</body>
</html>
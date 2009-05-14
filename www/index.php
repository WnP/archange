<?php

/*****************************************************************************
 * © 2009, Tuxce <tuxce.net@gmail.com>
 * Inspiré de http://krijnhoetmer.nl/irc-logs/
 * Log depuis le plugin ChannelLogger d'un supybot:
 * 	http://sourceforge.net/projects/supybot/
 *****************************************************************************
 */

$network = "freenode";
$network_url = "irc.freenode.net";
$channel = "#archlinux-fr";
$rep = "log/$network/$channel/";
$file_pre = "$channel.";
$file_post = ".log";
$title = "Logs IRC: $network / $channel / ";
$title_h1 = "Logs IRC: $network / <a href='" . $_SERVER['PHP_SELF']
	. "'>$channel</a> / ";


$files = null;
$last_files = null;
@$day = $_GET['day'];
@$month = $_GET['month'];
@$year = $_GET['year'];

if (!empty ($day) && 
	preg_match ("/([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])/", 
	$day, $matches))
{
	$year = $matches[1];
	$month = $matches[2];
	$day = $matches[3];
}

if (!empty ($month) && preg_match ("/([0-9][0-9][0-9][0-9])-([0-9][0-9])/", 
	$month, $matches))
{
	$year = $matches[1];
	$month = $matches[2];
}

if (empty ($year))
{
	$day = $month = null;
}

@$filter = $_GET['filter'];
@$hl = $_GET['hl'];

$display = 5;

function is_utf8($string) 
{

	// From http://w3.org/International/questions/qa-forms-utf-8.html
	return preg_match('%^(?:
		[\x09\x0A\x0D\x20-\x7E]            # ASCII
		| [\xC2-\xDF][\x80-\xBF]             # non-overlong 2-byte
		|  \xE0[\xA0-\xBF][\x80-\xBF]        # excluding overlongs
		| [\xE1-\xEC\xEE\xEF][\x80-\xBF]{2}  # straight 3-byte
		|  \xED[\x80-\x9F][\x80-\xBF]        # excluding surrogates
		|  \xF0[\x90-\xBF][\x80-\xBF]{2}     # planes 1-3
		| [\xF1-\xF3][\x80-\xBF]{3}          # planes 4-15
		|  \xF4[\x80-\x8F][\x80-\xBF]{2}     # plane 16
	)*$%xs', $string);

}


function get_files ()
{
	global $files, $rep;
	global $rep, $file_pre, $file_post;
	$files = array ();
	$handle=opendir($rep);
	while ($file = readdir($handle))
	{
		if (is_file($rep . $file) and $file != "index.php")
		{
			if (preg_match ("/^$file_pre([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])$file_post$/", 
				$file, $matches))
			{
				array_push ($files, $matches[1]);
			}
		}
	}
	closedir($handle);
	if (empty ($files)) return false;
	rsort ($files);
	return true;
}

function set_lines_number ()
{
	global $files, $last_files, $display;
	global $rep, $file_pre, $file_post;
	global $year, $month;
	$last_files = array ();
	$end = false;
	$begin = 0;
	if (empty ($files)) return false;
	if (!empty ($month))
	{
		// Si on affiche un mois, calcule l'index du premier et dernier fichier
		// du mois.
		// #TODO: la, je suppose que tout les mois ont au minimum le premier 
		// jour !
		$end = array_search (date ("Y-m-d", 
			mktime(0, 0, 0, $month, 1, $year)), $files);
		if ($end === false)
			$end = count ($files) - 1;
		$begin = array_search (date ("Y-m-d",
		   	mktime(0, 0, 0, $month + 1, 1, $year)), $files);
		if ($begin === false)
			$begin = 0;
		else
			$begin++;
		if ($end - $begin > 31) return false;
	}
	else
		// Si on n'affiche pas un mois, c'est les "$display" derniers fichiers.
		$end = $display - 1;

	if ($end === false) return false;


	if (!empty ($_POST['nicks']))
	{
		$nicks=split (",", $_POST['nicks']);
	}

	for ($i=$begin; $i<=$end; $i++)
	{
		$lines = file ($rep . $file_pre . $files[$i] . $file_post);
		if (!empty ($nicks))
		{
			$somme = 0;
			foreach ($lines as $line)
				foreach ($nicks as $nick)
					$somme += preg_match ("/$nick/i", $line);
			array_push ($last_files, array ($files[$i], count ($lines), 
				$somme));
		}
		else
			array_push ($last_files, array ($files[$i], count ($lines), "-"));
	}
	return true;
}



if (!empty ($month))
{
	$title .= "$year-$month";
	$title_h1 .= "<a href='?month=$year-$month'>$year-$month</a>";
}

if (!empty ($day))
{
	$title .= "-$day";
	$title_h1 .= "-$day";
}

?>

<!DOCTYPE html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title><?php echo $title; ?></title>
<script src="log.js"></script>
<link rel="stylesheet" href="log.css" type="text/css" />
</head>
<body>
<h1><?php echo $title_h1; ?></h1>

<?php
if (empty ($day))
{
	get_files();
	set_lines_number();
?>
<br/>
<!-- Partie Options -->
<div id="sidebar">
 <form method="post" >
  <fieldset>
   <legend>Options</legend>
	<label for="nicks">Vos pseudos</label>
	<input type="text" name="nicks" id="nicks"
	title="Exemple: am,stram,gram (l'espace compte)" 
	value="<?php echo (empty ($_POST['nicks'])) ? "" : $_POST['nicks']; ?>"> 
	<input type="submit" name="search" value="Chercher">
  </fieldset>
 </form>
</div>
<!-- Fin Partie Options -->


<!-- Liste des logs -->
<div id="<?php echo $channel; ?>" >
  <h2><a href="irc://<?php echo "$network_url/$channel"; ?>">
<?php echo $channel; ?></a></h2>
  <table>
	<tbody>
	  <tr>
		<th>Jour</th>
		<th><abbr title="Lignes">#</abbr></th>
		<th><abbr title="Nombre d'occurrences du (des) pseudo(s)">?</abbr></th>
	  </tr>
<?php
	foreach ($last_files as $file)
	{
		$url = "?day=" . $file[0];
		$urltext = substr ($file[0], 8, 2);
		$lines = $file[1];
		$found = $file[2];
		echo "<tr>";
		echo "<td><a href='$url'>$urltext</a></td>";
		echo "<td>$lines</td><td>$found</td></tr>\n";
	}
?>
	</tbody>
  </table>

<br/>
<h3>Archives</h3>
<ul>
<?php
	$month = "";
	foreach ($files as $file)
	{
		if ($month != substr ($file, 0, 7))
		{
			$month = substr ($file, 0, 7);
			echo "<li><a href='?month=$month'>$month</a></li>\n";
		}
	}
?>
</ul>
</div>
<!-- Fin Liste des logs -->
<?php
}
else
{
	// Le log d'un journée est demandé
?>
  <input id="hl_txt" value="<?php echo (empty ($hl)) ? "" : $hl; ?>" 
	type="text"> 
  <input id="hl_btn" value="Montrer" type="button"/><br/>
  <input id="status" type="checkbox" checked="checked"/>
  <label for="status">Cacher les messages join/part/quit</label>
  <br/>
  <br/>
  <ol id='lines'>
<?php
	$the_date = $year . "-" . $month . "-" . $day;
	if (is_file ($rep . $file_pre . $the_date . $file_post))
	{
		$lines = file ($rep . $file_pre . $the_date . $file_post);
		foreach ($lines as $line_num => $line) 
		{
			$classe = "";
			if (!empty ($filter) and (preg_match ("/$filter/i", $line) != 0))
				$classe="class='filtered'";
			if (!empty ($hl) and (preg_match ("/$hl/i", $line) != 0))
				$classe="class='hl'";
			if (strstr ($line, "]  ***") !== false)
				$classe="class='hide'";
			echo "<li $classe id='l-$line_num'><a href='#l-$line_num'>#</a>";
			if (! is_utf8 ($line))
				echo htmlspecialchars(utf8_encode ($line), 
					ENT_COMPAT, 'UTF-8');
			else
				echo htmlspecialchars($line, ENT_COMPAT, 'UTF-8');
			echo "</li>\n";
		}
	}
	echo "</ol>";
}
?>
</body>
</html>


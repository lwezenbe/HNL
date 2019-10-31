<html>
<head>
<title><?php $user = get_current_user(); echo str_replace('/eos/user/'.$user[0].'/'.$user.'/www','',getcwd()); ?></title>
<style type='text/css'>
body {
    font-family: "Helvetica", sans-serif;
    font-size: 9pt;
    line-height: 10.5pt;
}
h1 {
    font-size: 14pt;
    margin: 0.5em 1em 0.2em 1em;
    text-align: left;
    display: inline-block;
}
div.fixed {
    position: fixed;
    white-space: nowrap;
    width:100%;
}
div.bar {
    display: inline-block;
    margin: 0.5em 0.6em 0.2em 0.6em;
    padding: 10px;
    color: #29407C;
    background: white;
    text-align: center;
    border: 1px solid #29407C;
    border-radius: 5px;
}
div.barEmpty {
    color: #ccc;
    border: 1px solid #ccc;
}
a.bar {
    display: inline-block;
    margin: 0.5em 0.6em 0.2em 0.6em;
    padding: 10px;
    color: white;
    background: #29407C;
    text-align: center;
    border: 1px solid #29407C;
    border-radius: 5px;
}
a.bar:hover {
    background-color: #4CAF50;
    color: white;
}
div.pic h3 { 
    font-size: 11pt;
    margin: 0.5em 1em 0.2em 1em;
}
div.pic p {
    font-size: 11pt;
    margin: 0.0em 1em 0.2em 1em;
}
div.pic {
    display: block;
    float: left;
    background-color: white;
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 2px;
    text-align: center;
    margin: 40px 10px 10px 2px;
}
div.picRecent { border: 1px solid green; }
div.picAging  { border: 1px solid orange; }
div.picOld    { border: 1px solid red; }
div.list {
    font-size: 13pt;
    margin: 0.5em 1em 1.2em 1em;
    display: block; 
    clear: both;
}
div.list li {
    margin-top: 0.3em;
}
a { text-decoration: none; color: #29407C; }
a:hover { text-decoration: underline; color: #D08504; }
</style>
</head>
<body>
<div class="fixed">
<?php
  function showIfExists($path, $name){
    if(file_exists($path)){
      if(realpath('./')!=realpath($path)){
        $user = get_current_user();
        $webPath = str_replace('eos/user/'.$user[0].'/'.$user.'/www', $user, $path).'/?'.$_SERVER['QUERY_STRING'];
        $webPath = str_replace('storage_mnt/storage/user/'.$user.'/public_html', '~'.$user, $path).'/?'.$_SERVER['QUERY_STRING'];
        print "<span><a class=\"bar\" href=\"$webPath\">$name</a></span>";
      } else {
        print "<span><div class=\"bar\">$name</div></span>";
      }
    } else {
      print "<span><div class=\"bar barEmpty\">$name</div></span>";
    }
  }
  showIfExists('..', 'parent');

  $fullPath=realpath("./").'/';
  $channels=array('all','ee','emu','mumu','SF','all','noData');
  $myChannel=NULL;
  foreach($channels as $c){
    foreach(explode('/', $fullPath) as $subdir){
      if(strpos($subdir, $c)===0){
        $myChannelDir='/'.$subdir.'/';
        $temp=explode('-',$subdir);
        $myChannel=$temp[0];
      }
    }
  }

  function tryModifier($channelDir, $old, $new, $fullPath){
    $newChannelDir=str_replace($old, $new, $channelDir);
    $newPath      =str_replace($channelDir, $newChannelDir, $fullPath);
    if(file_exists(substr($newPath, 0, -1))) return $newPath;
    else                                     return NULL;
  }

  function modifyChannel($channelDir, $old, $new, $fullPath){
    if(!is_null($old)) return tryModifier($channelDir, $old, $new, $fullPath);
    if(strpos($channelDir, $new)!==false) return $fullPath;
    $tryAtEnd=tryModifier($channelDir, $channelDir, substr($channelDir, 0, -1).'-'.$new.'/', $fullPath);
    if(!is_null($tryAtEnd)) return $tryAtEnd;
    foreach(explode('-',$channelDir) as $sub){
      $tryInBetween=tryModifier($channelDir, $sub, $sub.'-'.$new, $fullPath);
      if(!is_null($tryInBetween)) return $tryInBetween;
    }
    return NULL;
  }

  if(!is_null($myChannel)){
    $logPath    = modifyChannel($myChannelDir, NULL,       'log',      $fullPath);
    $linPath    = modifyChannel($myChannelDir, '-log',     '',         $fullPath);
    $normPath   = modifyChannel($myChannelDir, NULL,       'normMC',   $fullPath);
    $lumiPath   = modifyChannel($myChannelDir, '-normMC',  '',         $fullPath);
    $sysPath    = modifyChannel($myChannelDir, NULL,       'sys',      $fullPath);
    $noSysPath  = modifyChannel($myChannelDir, '-sys',      '',        $fullPath);
    $postPath   = modifyChannel($myChannelDir, NULL,       'post',     $fullPath);
    $noPostPath = modifyChannel($myChannelDir, '-post',      '',       $fullPath);
    $eePath     = modifyChannel($myChannelDir, $myChannel, 'ee',       $fullPath);
    $mumuPath   = modifyChannel($myChannelDir, $myChannel, 'mumu',     $fullPath);
    $allPath    = modifyChannel($myChannelDir, $myChannel, 'all',      $fullPath);
    $emuPath    = modifyChannel($myChannelDir, $myChannel, 'emu',      $fullPath);
    $SFPath     = modifyChannel($myChannelDir, $myChannel, 'SF',       $fullPath);
    $noDataPath = modifyChannel($myChannelDir, $myChannel, 'noData',   $fullPath);

    function multipleOptions($options){
      $counter = 0;
      foreach($options as $o){
        if(file_exists($o)){
          $counter +=1;
        }
      }
      return ($counter > 1);
    }

    if(multipleOptions(array($logPath,$linPath))){
      showIfExists($logPath,   'logarithmic');
      showIfExists($linPath,   'linear');
    }
    if(multipleOptions(array($eePath,$emuPath,$mumuPath,$allPath,$SFPath,$noDataPath))){
      showIfExists($eePath,    'ee');
      showIfExists($emuPath,   'e&#956');
      showIfExists($mumuPath,  '&#956&#956');
      showIfExists($allPath,   'all');
      showIfExists($SFPath,    'SF');
      showIfExists($noDataPath,'no data');
    }
    if(multipleOptions(array($normPath,$lumiPath))){
      showIfExists($normPath,   'normalize to data');
      showIfExists($lumiPath,   'normalize to lumi');
    }
    if(multipleOptions(array($sysPath,$noSysPath))){
      showIfExists($noSysPath,  'no sys');
      showIfExists($sysPath,    'sys');
    }
    if(multipleOptions(array($postPath,$noPostPath))){
      showIfExists($noPostPath,  'pre-fit');
      showIfExists($postPath,    'post-fit');
    }
  }
?>
<span>
<h1><form>filter  <input type="text" name="match" size="25" value="<?php if (isset($_GET['match'])) print htmlspecialchars($_GET['match']);  ?>" /><input type="Submit" value="Go" /></form></h1>
</span>
</div>
<br style="clear:both" />
<div>
<pre style="font-size:80%">
<?php
  if(file_exists('info.txt')){
    print "<br /><br /><br />";
    echo file_get_contents('info.txt');
  }
?>
</pre>
</div>
<div>
<?php
$displayed = array();
if ($_GET['noplots']) {
    print "Plots will not be displayed.\n";
} else {
  function displayFigures($figExt, $displayed){
    $other_exts = array('.pdf', '.cxx', '.eps', '.root', '.txt', '.tex', '.C');
    $filenames = glob('*.'.$figExt); sort($filenames);
    $newest=0;
    foreach($filenames as $f){
      if(filemtime($f)>$newest) $newest=filemtime($f);
    }
    foreach ($filenames as $filename) {
        if (isset($_GET['match']) && !fnmatch('*'.$_GET['match'].'*', $filename)) continue;
        if (in_array($filename,$used)) continue;
        array_push($displayed, $filename);
        $name=str_replace('.'.$figExt, '', $filename);
        if      ($newest-filemtime($filename) > 240*3600){ print "<div class='pic picOld'>\n"; }
        else if ($newest-filemtime($filename) > 3  *3600){ print "<div class='pic picAging'>\n"; }
        else if (time()-filemtime($filename)  > 3  *3600){ print "<div class='pic'>\n"; }
        else                                             { print "<div class='pic picRecent'>\n"; }
       
        print "<h3><a href=\"$filename\">$name</a></h3>";
        print "<a href=\"$filename\"><img src=\"$filename\" style=\"border: none; width: 300px; \"></a>";
        $others = array();
        foreach ($other_exts as $ex) {
            $exNoDot=str_replace('.','',$ex);
            $other_filename = str_replace('.'.$figExt, $ex, $filename);
            array_push($displayed, $other_filename);
            if(file_exists($other_filename) and filemtime($filename)-filemtime($other_filename)<100){
              array_push($others, "<a class=\"file\" href=\"$other_filename\">[" . $exNoDot . "]</a>");
            }
        }

        $gitInfo = str_replace('.'.$figExt, '.gitInfo', $filename);
        array_push($displayed, $gitInfo);
        $pklFile = str_replace('.'.$figExt, '.pkl', $filename);
        array_push($displayed, $pklFile);
        if(file_exists($gitInfo) and filemtime($filename)-filemtime($gitInfo)<100){
          print "<p style='font-size:80%'>Modified: <a class=\"file\" href=\"$gitInfo\">".date ("F d Y H:i:s", filemtime($filename)) . "</a></p>";
        } else {
          print "<p style='font-size:80%'>Modified: ".date ("F d Y H:i:s", filemtime($filename)) . " </p>";
        }
        if ($others) print "<p>Also as ".implode(', ',$others)."</p>";
        print "</div>";
    }
    return $displayed;
  }
  $displayed = displayFigures('png', $displayed);
  $displayed = displayFigures('jpg', $displayed);
}
?>
</div>
<div class="list" style="margin-top: 2cm">
<ul>
<?php
$nondirs = array();
foreach (glob("*") as $filename) {
    if ($_GET['noplots'] || !in_array($filename, $displayed)) {
        if (isset($_GET['match']) && !fnmatch('*'.$_GET['match'].'*', $filename)) continue;
        if (fnmatch('*-normMC*', $filename)) continue;
        if (fnmatch('*-log*',    $filename)) continue;
        if (fnmatch('*-sys*',    $filename)) continue;
        if (is_dir($filename)) {
            print "<li>[DIR] <a href=\"$filename\">$filename</a></li>";
        } else if ($filename != "index.php" and $filename != "info.txt" and $filename != "git.txt") {
            array_push($nondirs,"<li><a href=\"$filename\">$filename</a></li>");
        }
    }
}
foreach ($nondirs as $file) {
    print $file;
}
?>
</ul>
</div>
</body>
</html>

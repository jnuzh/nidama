
<h1>淘宝应用开发</h1>

<p>应用获取用户mother_fun的资料</p>
<?php

?>
<?php
echo "<p>begin</p>";
header("Content-Type: text/html; charset=gb2312");
include("taobao_sdk/TopSdk.php");
$c = new TopClient;
$c->appkey = "1021741748";
$c->secretKey = "sandboxa301cddc44328d6a71817de9e";
$sessionKey="6102429a868d94a8144002bbc09b9e1b0e5e8160465e5013629363321";
$req = new UserGetRequest;
$req->setFields("nick,sex");
$resp = $c->execute($req, $sessionKey);
print_r($resp);
echo "<p>end</p>";
?>

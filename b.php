
<?php
header("Content-Type: text/html; charset=gb2312");
require_once 'util.php';
$appKey = 'test';
$appSecret = 'test';
//��������
$paramArr = array(
     'app_key' => $appKey,
     'method' => 'taobao.user.get',
     'format' => 'json',
     'v' => '2.0',
     'sign_method'=>'md5',
     'timestamp' => date('Y-m-d H:i:s'),
     'fields' => 'nick,type,buyer_credit,seller_credit',
     'nick' => 'sandbox_motherfun'
);
//����ǩ��
$sign = createSign($paramArr);
//��֯����
$strParam = createStrParam($paramArr);
$strParam .= 'sign='.$sign;
//���ʷ���
$url = 'http://gw.api.tbsandbox.com/router/rest?'.$strParam;

echo $url;
echo "<br><br>";
$result = file_get_contents($url);
$result = json_decode($result);
echo "json�ĽṹΪ:";
print_r($result);
echo "<br>";
echo "�û�����Ϊ:".$result->user_get_response->user->nick;
echo "<br>";
echo "������õȼ�Ϊ:".$result->user_get_response->user->buyer_credit->level;
?>





<?php
echo "<p>begin</p>";
header("Content-Type: text/html; charset=UTF-8");
include("taobao_sdk/TopSdk.php");
echo "<h1>TaobaoFun</h1>";

echo "<p>mother_fun</p>";


class MFRequest
{
    public $center;
    private $sessionKey;
    /*
    function __construct($appkey, $secretKey, $sessionKey){
    $center->appkey = $appkey;
    $center->secretKey=$secretKey;
    $center->sessionKey=$sessionKey;
    }
    */
    function __construct()
    {
        $this->center            = new TopClient;
        
        $this->center->appkey    = "1021759194";
        $this->center->secretKey = "sandbox28a555dbe54c7657fbd54a662";
        $this->sessionKey        = "6100a30c6566785168b046a153425d7cb88b0b1c5c0ef123629363321";
        
/*
        $this->center->appkey    = "test";
        $this->center->secretKey = "test";
        $this->sessionKey        = "61017067e623891a571080d4fcdae5f218f30a6999ccf3e3629363321";

*/
        
    }
    
    function setAppkey($appKey)
    {
        $this->center->appKey = $appKey;
        
    }
    
    function setSecretKey($secretKey)
    {
        $this->center->secretKey = $secretKey;
    }
    
    function setSessionKey($sessionKey)
    {
        $this->center->sessionKey = $sessionKey;
    }
    
    function shopGet()
    {
        $req = new ShopGetRequest;
        $req->setFields("sid,cid,title,nick,desc,bulletin,pic_path,created,modified");
        $req->setNick("sandbox_motherfun");
        $resp = $this->center->execute($req);
        return $resp->shop;
    }
    
    function userGet()
    {
        $req = new UserGetRequest;
        $req->setFields("user_id,uid,nick,sex,buyer_credit,seller_credit,location,created,last_visit,birthday,type,status,alipay_no,alipay_account,alipay_account,email,consumer_protection,alipay_bind");
        $req->setNick("sandbox_motherfun");
        $resp = $this->center->execute($req);
        return $resp->user;
    }
    
    function sellerGet()
    {
        $req = new UserSellerGetRequest;
        $req->setFields("user_id,nick,sex,seller_credit,type,has_more_pic,item_img_num,item_img_size,prop_img_num,prop_img_size,auto_repost,promoted_type,status,alipay_bind,consumer_protection,avatar,liangpin,sign_food_seller_promise,has_shop");
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp->user;
    }
    
    function itemsListGet()
    {
        $req = new ItemsListGetRequest;
        $req->setFields("detail_url,num_iid,title,nick,type,cid,seller_cids,props,input_pids,input_str,desc,pic_url,num,valid_thru,list_time,delist_time,stuff_status,location,price,post_fee,express_fee,ems_fee,has_discount,freight_payer,has_invoice,has_warranty,has_showcase,modified,increment,approve_status,postage_id,product_id,auction_point,property_alias,item_img,prop_img,sku,video,outer_id,is_virtual");
        $req->setNumIid(3838293428);
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp;
    }
    
    function itemsOnsaleGet()
    {
        $req = new ItemsOnsaleGetRequest;
        $req->setFields("approve_status,num_iid,title,nick,type,cid,pic_url,num,props,valid_thru,list_time,price,has_discount,has_invoice,has_warranty,has_showcase,modified,delist_time,postage_id,seller_cids,outer_id");
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp->items;
    }
    
    function itemsInventorGet()
    {
        $req = new ItemsInventoryGetRequest;
        $req->setFields("approve_status,num_iid,title,nick,type,cid,pic_url,num,props,valid_thru,list_time,price,has_discount,has_invoice,has_warranty,has_showcase,modified,delist_time,postage_id,seller_cids,outer_id");
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp->items;
    }
    function itemGet($numIid)
    {
        $req = new ItemGetRequest;
        $req->setFields("detail_url,num_iid,title,nick,type,cid,seller_cids,props,input_pids,input_str,desc,pic_url,num,valid_thru,list_time,delist_time,stuff_status,location,price,post_fee,express_fee,ems_fee,has_discount,freight_payer,has_invoice,has_warranty,has_showcase,modified,increment,approve_status,postage_id,product_id,auction_point,property_alias,item_img,prop_img,sku,video,outer_id,is_virtual");
        $req->setNumIid($numIid);
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp->item;
    }  
    
    function itemcatsAuthorizeGet()
    {
        $req = new ItemcatsAuthorizeGetRequest;
        $req->setFields("brand.vid,brand.name,item_cat.cid,item_cat.name,item_cat.status,item_cat.sort_order,item_cat.parent_cid,item_cat.is_parent");
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp;
    }
    
    function itemcatsGet()
    {
        $req = new ItemcatsGetRequest;
        $req->setFields("cid,parent_cid,name,is_parent");
        $req->setParentCid(0);
        $resp = $this->center->execute($req);
        return $resp->item_cats;
    }
    
    function itemAdd()
    {
        $req = new ItemAddRequest;
        $req->setNum(10);
        $req->setPrice("998");
        $req->setType("fixed");
        $req->setStuffStatus("new");
        $req->setTitle("É³Ïä²âÊÔ:ºÚÑÒÐ¡¿ãñÃ");
        $req->setDesc("ÃÈÃÃ×ÓµÚ¶þµ¯");
        $req->setLocationState("¹ã¶«");
        $req->setLocationCity("Öéº£");
        $req->setCid(18957);
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp;
    }
    
    function tmcMessagesConsume()
    {
        $req = new TmcMessagesConsumeRequest;
        $req->setQuantity(100);
        $resp = $this->center->execute($req);
        return $resp;
    }
    
    function tmcUserPermit(){
		$req = new TmcUserPermitRequest;
		$req->setTopics("taobao_item_ItemUpdate,taobao_item_ItemDelete ");
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp;
    }
     function itemDelete($numIid){
    $req = new ItemDeleteRequest;
$req->setNumIid($numIid);
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp;
	}
	
	function tmcUserGet(){
	$req = new TmcUserGetRequest;
$req->setFields("user_nick,topics,user_id,is_valid,created,modified");
$req->setNick("sandbox_motherfun");
  $resp = $this->center->execute($req);
  return $resp;
	}
	
	function tmcMessageProduce(){
	$req = new TmcMessageProduceRequest;
$req->setTopic("taobao_trade_TradeCreate");
$req->setContent("{'tid':2895732958732,'seller_nick':'sandbox_motherfun'}");
  $resp = $this->center->execute($req);
  return $resp;
	}
}


function echoInTable1($xml)
{
    echo $xml->getName() . "<br />";
    echo "<table border='1'>";
    foreach ($xml->children() as $child) {
        echo "<tr>";
        echo "<td>" . $child->getName() . "</td>";
        echo "<td>" . $child . "</td>";
        echo "</tr>";
    }
    echo "</table>";
}
function echoInTable2($xml)
{
    echo $xml->getName() . "<br />";
    echo "<table border='1'>";
    $top = $xml->children()[0];
    echo "<tr>";
    foreach ($top->children() as $child) {
        echo "<td>" . $child->getName() . "</td>";
    }
    echo "</tr>";
    foreach ($xml->children() as $child) {
        echo "<tr>";
        foreach ($child->children() as $info) {
            echo "<td>" . $info . "</td>";
        }
        echo "</tr>";
    }
    echo "</table>";
}

$request = new MFRequest();
//echoInTable1($request->requestForShop());

//echoInTable1($request->requestForUser());

//echoInTable1($request->requestForItem("2100509812221"));

//print_r($request->tmcMessageProduce());

    print_r($request->tmcUserGet());
set_time_limit(0);
while (true) {
//sleep(5);
    print_r($request->tmcMessagesConsume());
    echo "<br/>";
    ob_flush();
    flush();
    usleep(1000);

}
?>

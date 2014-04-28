<?php
include("taobao_sdk/TopSdk.php");
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
    function __construct($sessionKey)
    {
        $this->center            = new TopClient;
        
         $this->center->appkey    = "1021759194";
         $this->center->secretKey = "sandbox28a555dbe54c7657fbd54a662";
        // $this->sessionKey        = "6100a30c6566785168b046a153425d7cb88b0b1c5c0ef123629363321";
        $this->sessionKey        = $sessionKey;
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
    
    function shopGet($nick)
    {
        $req = new ShopGetRequest;
        $req->setFields("sid,cid,title,nick,desc,bulletin,pic_path,created,modified");
        $req->setNick($nick);
        $resp = $this->center->execute($req);
        return $resp->shop;
    }
    
    function userGet()
    {
        $req = new UserGetRequest;
        $req->setFields("user_id,uid,nick,sex,buyer_credit,seller_credit,location,created,last_visit,birthday,type,status,email");
        $resp = $this->center->execute($req, $this->sessionKey);
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
        //$req->setFields("approve_status,num_iid,title,nick,type,cid,pic_url,num,props,valid_thru,list_time,price,has_discount,has_invoice,has_warranty,has_showcase,modified,delist_time,postage_id,seller_cids,outer_id");
         $req->setFields("approve_status,num_iid,title,nick,cid,num,price,seller_cids,pic_url");
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
    
    function itemUpdate($numIid,$num){
        $req = new ItemUpdateRequest;
        $req->setNumIid($numIid);
        $req->setNum($num);
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp->item;
    }
    
    function itemUpdateTitle($numIid,$title){
        $req = new ItemUpdateRequest;
        $req->setNumIid($numIid);
        $req->setTitle($title);
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp->item;
    }
    
    function itemUpdateDelisting($numIid){
        $req = new ItemUpdateDelistingRequest;
        $req->setNumIid($numIid);
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp->item;
    }
    
    function itemUpdateListing($numIid,$num){
        $req = new ItemUpdateListingRequest;
        $req->setNumIid($numIid);
        $req->setNum($num);
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
        $req->setTitle("沙箱测试：学姐头部");
        $req->setDesc("这是学姐的头");
        $req->setLocationState("广东");
        $req->setLocationCity("珠海");
        $req->setCid(50000802);
        $req->setApproveStatus("instock"); 
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp;
    }
    
    function itemDelete($numIid){
        $req = new ItemDeleteRequest;
        $req->setNumIid($numIid);
        $resp = $this->center->execute($req, $this->sessionKey);
        return $resp;
	}
    
    function productAdd(){
    	$req = new ProductAddRequest;
        $req->setCid(21);
        $req->setOuterId("96330012");
        $req->setProps("pid:vid;pid:vid");
        $req->setBinds("pid:vid;pid:vid");
        $req->setSaleProps("pid:vid;pid:vid");
        $req->setCustomerProps("20000:优衣库:型号:001:632501:1234");
        $req->setPrice("200.07");
        //附件上传的机制参见PHP CURL文档，在文件路径前加@符号即可
        $req->setName("沙箱测试：笔记本");
        $req->setDesc("这是产品描述");
        $req->setMajor("true");
        $req->setMarketTime("2000-01-01 00:00:00");
        $req->setPropertyAlias("1627207:3232483:深深绿色");
        $req->setPackingList("说明书:1;耳机:1;充电器:1");
        $req->setMarketId("2");
        $req->setSellPt("明星同款");
        $req->setImage('@'. dirname(__FILE__).'/02.jpg');
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
?>
<?php
/*用户数据测试*/
echo '测试用户数据<br><br>';
echo "当前用户信用：" . $_user->credit . "<br>";
echo "当前用户好评率：" . $_user->goodRate . "<br>";
echo "当前用户id:   " . $_user->id . "<br>";
echo "当前用户昵称：" . $_user->nick . "<br>";
echo "用户注册时间：" . $_user->registrationDate . "<br>";
echo "当前用户国家：" . $_user->country . "<br>";
echo "当前用户省份：" . $_user->province . "<br>";
echo "当前用户城市：" . $_user->city . "<br><br>";


/*店铺数据测试*/
echo "<br><br>店铺数据测试<br><br>";
echo "当前店铺介绍：" . $_shop->introduction . "<br>";
echo "当前店铺公告：" . $_shop->bulettin . "<br>";
echo "当前店铺Id：" . $_shop->id . "<br>";
echo "当前店铺标题：" . $_shop->title . "<br>";


/*类目数据测试*/
echo "<br><br>店铺类目数据测试<br><br>";
/** 查询单个类目 */                                    
$shopCategory =  $shopCategoryManager->queryById(1);
echo "查询单个类目,结果:<br>";
showShopCategroy($shopCategory);
echo "<br>";
/** 查询子类目的 */
$shopCategories =  $shopCategoryManager->querySubCategories(1);
echo "查询子类目结果：<br>";
foreach($shopCategories as $shopCategory){
    showShopCategroy($shopCategory);
}
/** 查询所有的类目 */
$allShopCategories = $shopCategoryManager->queryAll();
foreach ($allShopCategories as $shopCategory) {
    showShopCategroy($shopCategory);
}
echo "<br>";

/**类目数据测试*/
echo "<br><br>商品数据测试<br><br>";
echo "查询单个宝贝<br>";
$item = $itemManager->queryById(1);
showItem($item);
echo "<br>";


echo "查询单个类目下的宝贝<br>";
$items = $itemManager->queryByCategory(1,'hotsell',10);
foreach($items as $item){
    showItem($item);
}


echo "通过ID列表批量查宝贝<br>";
$ids=array(1,2,3,4);
$items = $itemManager->queryByIds($ids,'hotsell');
foreach($items as $item){
    showItem($item);
}


echo "通过ID列表批量查宝贝<br>";
$items = $itemManager->queryByKeyword("shaosheng","hotsell",10);
foreach($items as $item){
    showItem($item);
}


/*friendLinkManager*/
echo "<br><br>友情链接接口测试<br><br>";
$friendLinks = $friendLinkManager->queryAllLinks();
foreach ($friendLinks as $friendLink) {
    showFriendLink($friendLink);
}

/*uriManager*/
echo "<br><br>URI测试<br><br>";
echo "搜索" . $uriManager->searchURI() . "<br>";
echo "评论URI" . $uriManager->rateURI() . "<br>";
echo "店铺介绍URI" . $uriManager->shopIntrURI() . "<br>";


/*店铺首页链接测试*/
echo"<br><br>店铺链接测试<br><br>";

$allLinks = $shopManager->getShopPageLinks();
foreach ($allLinks as $link) {
    showPageLink($link);
}



function showShopCategroy($shopCategory){
    echo "店铺类目Id:" . $shopCategory->id . "<br> ";
    echo "店铺类目名称:" . $shopCategory->name . "<br> ";
    echo "店铺类目图标:" . $shopCategory->iconUrl . "<br> ";
    echo "店铺类目父ID:" . $shopCategory->parentId . "<br> ";
    echo "店铺ID:" . $shopCategory->shopId . "<br> ";
}

function showItem($item){
    echo "宝贝类目ID：" . $item->id . "<br>";
    echo "宝贝的价格：" . $item->price . "<br>";
    echo "宝贝的价格：" . $item->title . "<br>";
    echo "宝贝的所有者ID：" . $item->ownerId . "<br>";
    echo "宝贝的图片URL：" . $item->picUrl . "<br>";
    echo "宝贝的收藏数量：" . $item->collectedCount . "<br>";
    echo "宝贝的销售量：".$item->soldCount."<br>";
    echo "宝贝的评论数：".$item->commentCount."<br>";
    echo "宝贝的店铺类目：".$item->shopCategoryId."<br>";
    echo "宝贝的商品类目：".$item->itemCategoryId."<br>";
}

function showPageLink($pagelink){
    echo "页面链接类型: " . $pagelink->text . "<br>";
    echo "页面链接名称: " . $pagelink->href . "<br>";
    echo "页面链接URI:  " . $pagelink->target . "<br>";
}

function showFriendLink($friendLink){
    echo "友情链接ID: " . $friendLink->id . "<br>";
    echo "友情链接用户名: " . $friendLink->userId . "<br>";
    echo "友情链接标题:  " . $friendLink->title . "<br>";
    echo "友情链接地址:  " . $friendLink->url . "<br>";
}
?>
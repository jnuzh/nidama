<?php
/*�û����ݲ���*/
echo '�����û�����<br><br>';
echo "��ǰ�û����ã�" . $_user->credit . "<br>";
echo "��ǰ�û������ʣ�" . $_user->goodRate . "<br>";
echo "��ǰ�û�id:   " . $_user->id . "<br>";
echo "��ǰ�û��ǳƣ�" . $_user->nick . "<br>";
echo "�û�ע��ʱ�䣺" . $_user->registrationDate . "<br>";
echo "��ǰ�û����ң�" . $_user->country . "<br>";
echo "��ǰ�û�ʡ�ݣ�" . $_user->province . "<br>";
echo "��ǰ�û����У�" . $_user->city . "<br><br>";


/*�������ݲ���*/
echo "<br><br>�������ݲ���<br><br>";
echo "��ǰ���̽��ܣ�" . $_shop->introduction . "<br>";
echo "��ǰ���̹��棺" . $_shop->bulettin . "<br>";
echo "��ǰ����Id��" . $_shop->id . "<br>";
echo "��ǰ���̱��⣺" . $_shop->title . "<br>";


/*��Ŀ���ݲ���*/
echo "<br><br>������Ŀ���ݲ���<br><br>";
/** ��ѯ������Ŀ */                                    
$shopCategory =  $shopCategoryManager->queryById(1);
echo "��ѯ������Ŀ,���:<br>";
showShopCategroy($shopCategory);
echo "<br>";
/** ��ѯ����Ŀ�� */
$shopCategories =  $shopCategoryManager->querySubCategories(1);
echo "��ѯ����Ŀ�����<br>";
foreach($shopCategories as $shopCategory){
    showShopCategroy($shopCategory);
}
/** ��ѯ���е���Ŀ */
$allShopCategories = $shopCategoryManager->queryAll();
foreach ($allShopCategories as $shopCategory) {
    showShopCategroy($shopCategory);
}
echo "<br>";

/**��Ŀ���ݲ���*/
echo "<br><br>��Ʒ���ݲ���<br><br>";
echo "��ѯ��������<br>";
$item = $itemManager->queryById(1);
showItem($item);
echo "<br>";


echo "��ѯ������Ŀ�µı���<br>";
$items = $itemManager->queryByCategory(1,'hotsell',10);
foreach($items as $item){
    showItem($item);
}


echo "ͨ��ID�б������鱦��<br>";
$ids=array(1,2,3,4);
$items = $itemManager->queryByIds($ids,'hotsell');
foreach($items as $item){
    showItem($item);
}


echo "ͨ��ID�б������鱦��<br>";
$items = $itemManager->queryByKeyword("shaosheng","hotsell",10);
foreach($items as $item){
    showItem($item);
}


/*friendLinkManager*/
echo "<br><br>�������ӽӿڲ���<br><br>";
$friendLinks = $friendLinkManager->queryAllLinks();
foreach ($friendLinks as $friendLink) {
    showFriendLink($friendLink);
}

/*uriManager*/
echo "<br><br>URI����<br><br>";
echo "����" . $uriManager->searchURI() . "<br>";
echo "����URI" . $uriManager->rateURI() . "<br>";
echo "���̽���URI" . $uriManager->shopIntrURI() . "<br>";


/*������ҳ���Ӳ���*/
echo"<br><br>�������Ӳ���<br><br>";

$allLinks = $shopManager->getShopPageLinks();
foreach ($allLinks as $link) {
    showPageLink($link);
}



function showShopCategroy($shopCategory){
    echo "������ĿId:" . $shopCategory->id . "<br> ";
    echo "������Ŀ����:" . $shopCategory->name . "<br> ";
    echo "������Ŀͼ��:" . $shopCategory->iconUrl . "<br> ";
    echo "������Ŀ��ID:" . $shopCategory->parentId . "<br> ";
    echo "����ID:" . $shopCategory->shopId . "<br> ";
}

function showItem($item){
    echo "������ĿID��" . $item->id . "<br>";
    echo "�����ļ۸�" . $item->price . "<br>";
    echo "�����ļ۸�" . $item->title . "<br>";
    echo "������������ID��" . $item->ownerId . "<br>";
    echo "������ͼƬURL��" . $item->picUrl . "<br>";
    echo "�������ղ�������" . $item->collectedCount . "<br>";
    echo "��������������".$item->soldCount."<br>";
    echo "��������������".$item->commentCount."<br>";
    echo "�����ĵ�����Ŀ��".$item->shopCategoryId."<br>";
    echo "��������Ʒ��Ŀ��".$item->itemCategoryId."<br>";
}

function showPageLink($pagelink){
    echo "ҳ����������: " . $pagelink->text . "<br>";
    echo "ҳ����������: " . $pagelink->href . "<br>";
    echo "ҳ������URI:  " . $pagelink->target . "<br>";
}

function showFriendLink($friendLink){
    echo "��������ID: " . $friendLink->id . "<br>";
    echo "���������û���: " . $friendLink->userId . "<br>";
    echo "�������ӱ���:  " . $friendLink->title . "<br>";
    echo "�������ӵ�ַ:  " . $friendLink->url . "<br>";
}
?>
<div class="J_TRegion">
    <?php
    $sub_modules = array(
    array('id' => 'side_sales', domId => "detail_left-1"), // �Զ���ģ��
    array('shortname' => 'shop.itemCategory', 'version' => '1.0-common', domId => "detail_left-2"),
    array('shortname' => 'shop.searchInShop', 'version' => '1.0-common', domId => "detail_left_3"),
    array('id' => 'side_help', domId => "detail_left_4"), // �Զ���ģ��
    array('shortname' => 'shop.topList', 'version' => '1.0-common', domId => "detail_left_5")
);
    echo include_modules('sub-modules', $sub_modules);
    ?>
</div>
<div class="layout grid-s5m0">
    <div class="col-main">
        <div class="main-wrap J_TRegion">

            <?php

            $main_modules = array(

                array('shortname' => 'shop.picRound', 'version' => '1.0-common', domId => "index-01"),
                array('id' => 'floor', domId => "index-200"), // 自定义模块
                array('shortname' => 'shop.manualSpread', 'version' => '1.0-wangpu', domId => "index-02"),
                array('shortname' => 'shop.searchInShop', 'version' => '1.0-common', domId => "index-03"),
                array('id' => 'floor', domId => "index-201"), // 自定义模块
                array('shortname' => 'shop.itemRecommend', 'version' => '1.0-wangpu', domId => "index-04"),
                array('shortname' => 'shop.flashBanner', 'version' => '1.0-common', domId => "index-05"),
                array('shortname' => 'shop.forumShow', 'version' => '1.0-common', domId => "index-06"),
                array('id' => 'quick_join', domId => "index-202") // 自定义模块
            );

            echo include_modules('main-modules', $main_modules);

            ?>

        </div>
    </div>

    <div class="col-sub J_TRegion">

        <?php

        $sub_modules = array(
            array('id' => 'side_sales', domId => "index-300"), // 自定义模块
            array('shortname' => 'shop.itemCategory', 'version' => '1.0-common', domId => "index-101"),
            array('shortname' => 'shop.fileList', 'version' => '1.0-common', domId => "index-104"),
            array('shortname' => 'shop.searchInShop', 'version' => '1.0-common', domId => "index-105"),
            array('id' => 'side_help', domId => "index-301"), // 自定义模块
            array('shortname' => 'shop.topList', 'version' => '1.0-common', domId => "index-106"),
            array('shortname' => 'shop.friendLink', 'version' => '1.0-common', domId => "index-107")
        );

        echo include_modules('sub-modules', $sub_modules);

        ?>

    </div>
</div>
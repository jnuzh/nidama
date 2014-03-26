<div class="layout grid-s5m0">
	<div class="col-main">
		<div class="main-wrap J_TRegion" >

			<?
				echo include_modules('main-modules', array());
			?>

		</div>
	</div>

	<div class="col-sub J_TRegion">

		<?php

			$sub_modules = array(
				array('id' => 'side_sales', domId => "onsale-1"),	// 自定义模块
				array('shortname' => 'shop.itemCategory', 'version' => '1.0-common', domId => "onsale-2"),
				array('shortname' => 'shop.searchInShop', 'version' => '1.0-common', domId => "onsale-3"),
				array('id' => 'side_help',  domId => "onsale-4"),	// 自定义模块
				array('shortname' => 'shop.topList', 'version' => '1.0-common', domId => "onsale-5")
			);

			echo include_modules('sub-modules', $sub_modules);

		?>
	</div>
</div>
<div class="layout grid-s5m0">
	<div class="col-main">
		<div class="main-wrap J_TRegion">

			<?php

				$main_modules = array(
					array('shortname' => 'shop.searchList', 'version' => '1.0-wangpu', domId => "search-1")
				);
				echo include_modules('main-modules', $main_modules);

			?>

		</div>
	</div>

	<div class="col-sub J_TRegion">

		<?php

			$sub_modules = array(
				array('id' => 'side_sales', domId => "search-2"),	// 自定义模块
				array('shortname' => 'shop.itemCategory', 'version' => '1.0-common', domId => "search-3"),
				array('shortname' => 'shop.searchInShop', 'version' => '1.0-common', domId => "search-4"),
				array('id' => 'side_help',  domId => "search-5"),	// 自定义模块
				array('shortname' => 'shop.topList', 'version' => '1.0-common', domId => "search-6")
			);

			echo include_modules('sub-modules', $sub_modules);

		?>
	</div>
</div>	
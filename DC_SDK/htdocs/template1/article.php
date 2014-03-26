<div class="layout grid-s5m0">
	<div class="col-main">
		<div class="main-wrap J_TRegion">

			<?
				$main_modules = array(
					// �����б�
					array('shortname' => 'shop.fileList', 'version' => '1.0-common', domId => "article-1"),
					array('shortname' => 'shop.fileListDefault', 'version' => '1.0-common', domId => "article-2")

				);

				echo include_modules('main-modules', $main_modules);
			?>

		</div>
	</div>

	<div class="col-sub J_TRegion">

		<?php

			$sub_modules = array(
				array('id' => 'side_sales', domId => "article-3"),	// �Զ���ģ��
				array('shortname' => 'shop.fileList', 'version' => '1.0-common', domId => "article-4"),
				array('shortname' => 'shop.itemCategory', 'version' => '1.0-common', domId => "article-5"),
				// ����Ŀ¼
				array('shortname' => 'shop.fileDir', 'version' => '1.0-common', domId => "article-6"),
				// ����Ŀ¼ Ĭ��
				array('shortname' => 'shop.fileDirDefault', 'version' => '1.0-common', domId => "article-7"),
				array('shortname' => 'shop.fileSearch', 'version' => '1.0-common', domId => "article-8"),
				array('id' => 'side_help',  domId => "article-9"),	// �Զ���ģ��
				array('shortname' => 'shop.topList', 'version' => '1.0-common', domId => "article-10")
			);

			echo include_modules('sub-modules', $sub_modules);
		?>
	</div>
</div>
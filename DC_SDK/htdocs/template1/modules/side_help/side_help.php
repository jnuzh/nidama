<div class="box J_TBox" <?php echo $_MODULE_TOOLBAR ?>>
	<div class="buy-help">
		<div class="hd"><h3><span>ЙКТђАяжњ</span></h3></div>
		<div class="bd">
			<ul>
				<?
					for ( $i = 0; $i < 5; $i++ ) {
						if ( $_MODULE['ww_' . $i] ) {
							echo '<li>'. $_MODULE['ww_' . $i] .'</li>';
						}
					}
				?>
			</ul>
			<strong><em>зЂвт</em>ЪТЯю</strong>
			<ol>
				<?
					for ( $i = 0; $i < 5; $i++ ) {
						if ( $_MODULE['li_' . $i] ) {
							echo '<li>'. $_MODULE['li_' . $i] .'</li>';
						}
					}
				?>
			</ol>
			<p><img src="<? echo $_MODULE['img']; ?>" /></p>
		</div>
	</div>
</div>
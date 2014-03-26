<div class="box J_TBox" <?php echo $_MODULE_TOOLBAR ?>>
	<div class="floor">
		<div class="bd">
			<div class="slide">
				<p class="slide-main">
					<?
						if ($_MODULE["img_1"]) {
							echo '<a href="'. $_MODULE["link_1"] .'"><img width="512" height="260" src="'.$_MODULE["img_1"].'" /></a>';
						}
					?>
				</p>
			</div>
			<div class="carousel J_TWidget" data-widget-type="Carousel" data-widget-config="{'effect':'scrollx','easing':'easeOutStrong','prevBtnCls':'prev','nextBtnCls':'next', 'contentCls': 'carousel-main', 'navCls': 'carousel-nav','activeTriggerCls': 'selected'}">
				<span class="prev">prev</span>
				<span class="next">next</span>
				<div class="carousel-content">
					<p class="carousel-main">
						<?
							for ( $i = 0; $i < 4; $i++ ) {
								if ( $_MODULE['carousel_img_' . $i] ) {
									echo '<a target="_blank" href="'. $_MODULE['carousel_link_' . $i] .'"><img width="160" height="160" src="'. $_MODULE['carousel_img_' . $i] .'"></a>';
								}
							}
						?>
					</p>
				</div>
				<ul class="carousel-nav">
					<?
						for ( $i = 0; $i < 4; $i++ ) {
							if ( $_MODULE['carousel_nav_img_' . $i] ) {
								echo '<li'. ($i == 0  ? ' class="selected"' : "") .'><b></b><img src="'. $_MODULE['carousel_nav_img_' . $i] .'" /></li>';
							}
						}
					?>
				</ul>
			</div>
		</div>
	</div>
</div>
<div class="box J_TBox" <?php echo $_MODULE_TOOLBAR ?>>
	<div class="side-sales">
		<div class="hd"><h3><span>´ÙÏú»î¶¯</span></h3></div>
		<div class="bd">
			<div class="carousel J_TWidget" data-widget-type="Carousel" data-widget-config="{'effect':'scrollx','easing':'easeOutStrong','prevBtnCls':'prev','nextBtnCls':'next', 'contentCls': 'carousel-main', 'navCls': 'carousel-nav','activeTriggerCls': 'selected', 'lazyDataType':'img-src'}">
				<span class="prev">prev</span>
				<span class="next">next</span>
				<div class="carousel-content">
					<p class="carousel-main">
						<a target="_blank" href="#"><img width="160" height="160" src="http://img02.taobaocdn.com/tps/i2/T1xGRJXeVxXXXXXXXX-160-160.png"></a>
						<a target="_blank" href="#"><img width="160" height="160" src="http://img03.taobaocdn.com/tps/i3/T1OaRJXaJxXXXXXXXX-160-160.png"></a>
						<a target="_blank" href="#"><img width="160" height="160" src="http://img02.taobaocdn.com/tps/i2/T1xGRJXeVxXXXXXXXX-160-160.png"></a>
						<a target="_blank" href="#"><img width="160" height="160" src="http://img03.taobaocdn.com/tps/i3/T1OaRJXaJxXXXXXXXX-160-160.png"></a>
						<?
							for ($i = 0; $i < 5; $i++) {
								echo '<a target="_blank" href="'. $_MODULE['sales_link_' . $i] .'"><img width="160" height="160" src="'. $_MODULE['sales_img_' . $i] .'"></a>';
							}
						?>
					</p>
				</div>
			</div>
		</div>
	</div>
</div>
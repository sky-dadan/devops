jQuery(document).ready(function(){

	// === Sidebar navigation === //

	jQuery('.submenu > a').click(function(e)
	{
		e.preventDefault();
		var submenu = jQuery(this).siblings('ul');
		var li = jQuery(this).parents('li');
		//var submenus = jQuery('#sidebar li.submenu ul');
		//var submenus_parents = jQuery('#sidebar li.submenu');
		var submenus_arrow = jQuery(this).children('span.arrow');
		if(li.hasClass('open'))
		{
			if((jQuery(window).width() > 768) || (jQuery(window).width() < 479)) {
				submenu.slideUp();
			} else {
				submenu.fadeOut(250);
			}
			li.removeClass('open');
			submenus_arrow.removeClass("icon-chevron-down").addClass("icon-chevron-left");
		} else {
			if((jQuery(window).width() > 768) || (jQuery(window).width() < 479)) {
				//submenus.slideUp();
				submenu.slideDown();
			} else {
				//submenus.fadeOut(250);
				submenu.fadeIn(250);
			}
			//submenus_parents.removeClass('open');
			li.addClass('open');
			submenus_arrow.removeClass("icon-chevron-left").addClass("icon-chevron-down");
		}
	});

	var ul = jQuery('#sidebar > ul');

	jQuery('#sidebar > a').click(function(e)
	{
		e.preventDefault();
		var sidebar = jQuery('#sidebar');
		if(sidebar.hasClass('open'))
		{
			sidebar.removeClass('open');
			ul.slideUp(250);
		} else {
			sidebar.addClass('open');
			ul.slideDown(250);
		}
	});

	// === Resize window related === //
	jQuery(window).resize(function()
	{
		if(jQuery(window).width() > 479)
		{
			ul.css({'display':'block'});
			jQuery('#content-header .btn-group').css({width:'auto'});
		}
		if(jQuery(window).width() < 479)
		{
			ul.css({'display':'none'});
			fix_position();
		}
		if(jQuery(window).width() > 768)
		{
			jQuery('#user-nav > ul').css({width:'auto',margin:'0'});
            jQuery('#content-header .btn-group').css({width:'auto'});
		}
	});

	if(jQuery(window).width() < 468)
	{
		ul.css({'display':'none'});
		fix_position();
	}

	if(jQuery(window).width() > 479)
	{
	   jQuery('#content-header .btn-group').css({width:'auto'});
		ul.css({'display':'block'});
	}

	// === Tooltips === //
	jQuery('.tip').tooltip();
	jQuery('.tip-left').tooltip({ placement: 'left' });
	jQuery('.tip-right').tooltip({ placement: 'right' });
	jQuery('.tip-top').tooltip({ placement: 'top' });
	jQuery('.tip-bottom').tooltip({ placement: 'bottom' });

	// === Search input typeahead === //
	jQuery('#search input[type=text]').typeahead({
		source: ['Dashboard','Form elements','Common Elements','Validation','Wizard','Buttons','Icons','Interface elements','Support','Calendar','Gallery','Reports','Charts','Graphs','Widgets'],
		items: 4
	});

	// === Fixes the position of buttons group in content header and top user navigation === //
	function fix_position()
	{
		var uwidth = jQuery('#user-nav > ul').width();
		jQuery('#user-nav > ul').css({width:uwidth,'margin-left':'-' + uwidth / 2 + 'px'});

        var cwidth = jQuery('#content-header .btn-group').width();
        jQuery('#content-header .btn-group').css({width:cwidth,'margin-left':'-' + uwidth / 2 + 'px'});
	}

	// === Style switcher === //
	jQuery('#style-switcher i').click(function()
	{
		if(jQuery(this).hasClass('open'))
		{
			jQuery(this).parent().animate({marginRight:'-=190'});
			jQuery(this).removeClass('open');
		} else
		{
			jQuery(this).parent().animate({marginRight:'+=190'});
			jQuery(this).addClass('open');
		}
		jQuery(this).toggleClass('icon-arrow-left');
		jQuery(this).toggleClass('icon-arrow-right');
	});

	jQuery('#style-switcher a').click(function()
	{
		var style = jQuery(this).attr('href').replace('#','');
		jQuery('.skin-color').attr('href','css/maruti.'+style+'.css');
		jQuery(this).siblings('a').css({'border-color':'transparent'});
		jQuery(this).css({'border-color':'#aaaaaa'});
	});

	jQuery('.lightbox_trigger').click(function(e) {

		e.preventDefault();

		var image_href = jQuery(this).attr("href");

		if (jQuery('#lightbox').length > 0) {

			jQuery('#imgbox').html('<img src="' + image_href + '" /><p><i class="icon-remove icon-white"></i></p>');

			jQuery('#lightbox').slideDown(500);
		}

		else {
			var lightbox =
			'<div id="lightbox" style="display:none;">' +
				'<div id="imgbox"><img src="' + image_href +'" />' +
					'<p><i class="icon-remove icon-white"></i></p>' +
				'</div>' +
			'</div>';

			jQuery('body').append(lightbox);
			jQuery('#lightbox').slideDown(500);
		}

	});


	jQuery('#lightbox').live('click', function() {
		jQuery('#lightbox').hide(200);
	});

});


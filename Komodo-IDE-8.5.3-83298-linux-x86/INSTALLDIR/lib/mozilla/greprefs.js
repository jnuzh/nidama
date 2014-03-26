/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

pref("security.tls.version.min", 0);
pref("security.tls.version.max", 1);
pref("security.enable_tls_session_tickets", true);
pref("security.enable_md5_signatures", false);

pref("security.ssl.allow_unrestricted_renego_everywhere__temporarily_available_pref", false);
pref("security.ssl.renego_unrestricted_hosts", "");
pref("security.ssl.treat_unsafe_negotiation_as_broken", false);
pref("security.ssl.require_safe_negotiation",  false);
pref("security.ssl.warn_missing_rfc5746",  1);
pref("security.ssl.enable_false_start", false);

pref("security.ssl3.rsa_rc4_128_md5", true);
pref("security.ssl3.rsa_rc4_128_sha", true);
pref("security.ssl3.rsa_fips_des_ede3_sha", true);
pref("security.ssl3.rsa_des_ede3_sha", true);
pref("security.ssl3.dhe_rsa_camellia_256_sha", true);
pref("security.ssl3.dhe_dss_camellia_256_sha", true);
pref("security.ssl3.rsa_camellia_256_sha", true);
pref("security.ssl3.dhe_rsa_camellia_128_sha", true);
pref("security.ssl3.dhe_dss_camellia_128_sha", true);
pref("security.ssl3.rsa_camellia_128_sha", true);
pref("security.ssl3.dhe_rsa_aes_256_sha", true);
pref("security.ssl3.dhe_dss_aes_256_sha", true);
pref("security.ssl3.rsa_aes_256_sha", true);
pref("security.ssl3.ecdhe_ecdsa_aes_256_sha", true);
pref("security.ssl3.ecdhe_ecdsa_aes_128_sha", true);
pref("security.ssl3.ecdhe_ecdsa_des_ede3_sha", true);
pref("security.ssl3.ecdhe_ecdsa_rc4_128_sha", true);
pref("security.ssl3.ecdhe_rsa_aes_256_sha", true);
pref("security.ssl3.ecdhe_rsa_aes_128_sha", true);
pref("security.ssl3.ecdhe_rsa_des_ede3_sha", true);
pref("security.ssl3.ecdhe_rsa_rc4_128_sha", true);
pref("security.ssl3.ecdh_ecdsa_aes_256_sha", true);
pref("security.ssl3.ecdh_ecdsa_aes_128_sha", true);
pref("security.ssl3.ecdh_ecdsa_des_ede3_sha", true);
pref("security.ssl3.ecdh_ecdsa_rc4_128_sha", true);
pref("security.ssl3.ecdh_rsa_aes_256_sha", true);
pref("security.ssl3.ecdh_rsa_aes_128_sha", true);
pref("security.ssl3.ecdh_rsa_des_ede3_sha", true);
pref("security.ssl3.ecdh_rsa_rc4_128_sha", true);
pref("security.ssl3.dhe_rsa_aes_128_sha", true);
pref("security.ssl3.dhe_dss_aes_128_sha", true);
pref("security.ssl3.rsa_aes_128_sha", true);
pref("security.ssl3.dhe_rsa_des_ede3_sha", true);
pref("security.ssl3.dhe_dss_des_ede3_sha", true);
pref("security.ssl3.rsa_seed_sha", true);

pref("security.default_personal_cert",   "Ask Every Time");
pref("security.remember_cert_checkbox_default_setting", true);
pref("security.ask_for_password",        0);
pref("security.password_lifetime",       30);

pref("security.OCSP.enabled", 1);
pref("security.OCSP.require", false);
/* -*- Mode: Java; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 2 -*- */
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/* The prefs in this file are shipped with the GRE and should apply to all
 * embedding situations. Application-specific preferences belong somewhere else,
 * for example xpfe/bootstrap/browser-prefs.js
 *
 * Platform-specific #ifdefs at the end of this file override the generic
 * entries at the top.
 */

/*
 * SYNTAX HINTS:
 *
 *  - Dashes are delimiters; use underscores instead.
 *  - The first character after a period must be alphabetic.
 *  - Computed values (e.g. 50 * 1024) don't work.
 */

pref("keyword.enabled", false);
pref("general.useragent.locale", "chrome://global/locale/intl.properties");
pref("general.useragent.compatMode.firefox", false);

// This pref exists only for testing purposes. In order to disable all
// overrides by default, don't initialize UserAgentOverrides.jsm.
pref("general.useragent.site_specific_overrides", true);

// This pref controls whether or not to enable UA overrides in the
// product code that end users use (as opposed to testing code).
pref("general.useragent.enable_overrides", false);

pref("general.config.obscure_value", 13); // for MCD .cfg files

pref("general.warnOnAboutConfig", true);

// maximum number of dated backups to keep at any time
pref("browser.bookmarks.max_backups",       5);

pref("browser.cache.disk.enable",           true);
// Is this the first-time smartsizing has been introduced?
pref("browser.cache.disk.smart_size.first_run", true);
// Does the user want smart-sizing?
pref("browser.cache.disk.smart_size.enabled", true);
// Which max value should we use for smart-sizing?
pref("browser.cache.disk.smart_size.use_old_max", true);
// Size (in KB) explicitly set by the user. Used when smart_size.enabled == false
pref("browser.cache.disk.capacity",         256000);
// Max-size (in KB) for entries in disk cache. Set to -1 for no limit.
// (Note: entries bigger than 1/8 of disk-cache are never cached)
pref("browser.cache.disk.max_entry_size",    51200);  // 50 MB
pref("browser.cache.memory.enable",         true);
// -1 = determine dynamically, 0 = none, n = memory capacity in kilobytes
//pref("browser.cache.memory.capacity",     -1);
// Max-size (in KB) for entries in memory cache. Set to -1 for no limit.  
// (Note: entries bigger than than 90% of the mem-cache are never cached)
pref("browser.cache.memory.max_entry_size",  5120);
pref("browser.cache.disk_cache_ssl",        true);
// 0 = once-per-session, 1 = each-time, 2 = never, 3 = when-appropriate/automatically
pref("browser.cache.check_doc_frequency",   3);

pref("browser.cache.offline.enable",           true);

// offline cache capacity in kilobytes
pref("browser.cache.offline.capacity",         512000);

// the user should be warned if offline app disk usage exceeds this amount
// (in kilobytes)
pref("offline-apps.quota.warn",        51200);

// zlib compression level used for cache compression:
// 0 => disable compression
// 1 => best speed
// 9 => best compression
// cache compression turned off for now - see bug #715198
pref("browser.cache.compression_level", 0);

// Whether or not indexedDB is enabled.
pref("dom.indexedDB.enabled", true);
// Space to allow indexedDB databases before prompting (in MB).
pref("dom.indexedDB.warningQuota", 50);

// Whether or not Web Workers are enabled.
pref("dom.workers.enabled", true);
// The number of workers per domain allowed to run concurrently.
pref("dom.workers.maxPerDomain", 20);

// Whether nonzero values can be returned from performance.timing.*
pref("dom.enable_performance", true);

// Whether the Gamepad API is enabled
//@line 94 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("dom.gamepad.enabled", false);
pref("dom.gamepad.non_standard_events.enabled", false);
//@line 100 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Fastback caching - if this pref is negative, then we calculate the number
// of content viewers to cache based on the amount of available memory.
pref("browser.sessionhistory.max_total_viewers", -1);

pref("ui.use_native_colors", true);
pref("ui.click_hold_context_menus", false);
pref("browser.display.use_document_fonts",  1);  // 0 = never, 1 = quick, 2 = always
pref("browser.display.use_document_colors", true);
pref("browser.display.use_system_colors",   false);
pref("browser.display.foreground_color",    "#000000");
pref("browser.display.background_color",    "#FFFFFF");
pref("browser.display.force_inline_alttext", false); // true = force ALT text for missing images to be layed out inline
// 0 = no external leading, 
// 1 = use external leading only when font provides, 
// 2 = add extra leading both internal leading and external leading are zero
pref("browser.display.normal_lineheight_calc_control", 2);
pref("browser.display.show_image_placeholders", true); // true = show image placeholders while image is loaded and when image is broken
// min font device pixel size at which to turn on high quality
pref("browser.display.auto_quality_min_font_size", 20);
pref("browser.anchor_color",                "#0000EE");
pref("browser.active_color",                "#EE0000");
pref("browser.visited_color",               "#551A8B");
pref("browser.underline_anchors",           true);
pref("browser.enable_automatic_image_resizing", false);
pref("browser.enable_click_image_resizing", true);

// See http://dev.w3.org/html5/spec/forms.html#attr-fe-autofocus
pref("browser.autofocus", true);

// See http://whatwg.org/specs/web-apps/current-work/#ping
pref("browser.send_pings", false);
pref("browser.send_pings.max_per_link", 1);           // limit the number of pings that are sent per link click
pref("browser.send_pings.require_same_host", false);  // only send pings to the same host if this is true

pref("browser.display.use_focus_colors",    false);
pref("browser.display.focus_background_color", "#117722");
pref("browser.display.focus_text_color",     "#ffffff");
pref("browser.display.focus_ring_width",     1);
pref("browser.display.focus_ring_on_anything", false);
// focus ring border style.
// 0 = solid border, 1 = dotted border
pref("browser.display.focus_ring_style", 1);

pref("browser.helperApps.alwaysAsk.force",  false);
pref("browser.helperApps.neverAsk.saveToDisk", "");
pref("browser.helperApps.neverAsk.openFile", "");

// xxxbsmedberg: where should prefs for the toolkit go?
pref("browser.chrome.toolbar_tips",         true);
// 0 = Pictures Only, 1 = Text Only, 2 = Pictures and Text
pref("browser.chrome.toolbar_style",        2);
// max image size for which it is placed in the tab icon for tabbrowser.
// if 0, no images are used for tab icons for image documents.
pref("browser.chrome.image_icons.max_size", 1024);

pref("browser.triple_click_selects_paragraph", true);

// Media cache size in kilobytes
pref("media.cache_size", 512000);

// Master HTML5 media volume scale.
pref("media.volume_scale", "1.0");

// Timeout for wakelock release
pref("media.wakelock_timeout", 2000);

//@line 173 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("media.raw.enabled", true);
//@line 176 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("media.ogg.enabled", true);
//@line 179 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("media.opus.enabled", true);
//@line 182 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("media.wave.enabled", true);
//@line 185 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("media.webm.enabled", true);
//@line 194 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("media.navigator.enabled", true);
pref("media.navigator.video.default_width",640);
pref("media.navigator.video.default_height",480);
pref("media.navigator.video.default_fps",30);
pref("media.navigator.video.default_minfps",10);
pref("media.peerconnection.enabled", true);
pref("media.navigator.permission.disabled", false);
pref("media.peerconnection.default_iceservers", "[{\"url\": \"stun:23.21.150.121\"}]");
pref("media.peerconnection.use_document_iceservers", true);
// These values (aec, agc, and noice) are from media/webrtc/trunk/webrtc/common_types.h
// kXxxUnchanged = 0, kXxxDefault = 1, and higher values are specific to each 
// setting (for Xxx = Ec, Agc, or Ns).  Defaults are all set to kXxxDefault here.
pref("media.peerconnection.turn.disable", false);
pref("media.peerconnection.aec_enabled", true);
pref("media.peerconnection.aec", 1);
pref("media.peerconnection.agc_enabled", false);
pref("media.peerconnection.agc", 1);
pref("media.peerconnection.noise_enabled", false);
pref("media.peerconnection.noise", 1);
//@line 218 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
// TextTrack support
pref("media.webvtt.enabled", false);

//@line 222 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("media.webspeech.recognition.enable", false);
//@line 224 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Whether to enable Web Audio support
pref("media.webaudio.enabled", false);

// Whether to autostart a media element with an |autoplay| attribute
pref("media.autoplay.enabled", true);

// The default number of decoded video frames that are enqueued in
// MediaDecoderReader's mVideoQueue.
pref("media.video-queue.default-size", 10);

// Whether to enable the audio writing APIs on the audio element
pref("media.audio_data.enabled", true);

//@line 245 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// 0 = Off, 1 = Full, 2 = Tagged Images Only. 
// See eCMSMode in gfx/thebes/gfxPlatform.h
pref("gfx.color_management.mode", 2);
pref("gfx.color_management.display_profile", "");
pref("gfx.color_management.rendering_intent", 0);
pref("gfx.color_management.enablev4", false);

pref("gfx.downloadable_fonts.enabled", true);
pref("gfx.downloadable_fonts.fallback_delay", 3000);

pref("gfx.filter.nearest.force-enabled", false);

// prefs controlling the font (name/cmap) loader that runs shortly after startup
//@line 264 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("gfx.font_loader.families_per_slice", 3); // read in info 3 families at a time
pref("gfx.font_loader.delay", 8000);           // 8 secs after startup
pref("gfx.font_loader.interval", 50);          // run every 50 ms
//@line 268 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// whether to always search all font cmaps during system font fallback
pref("gfx.font_rendering.fallback.always_use_cmaps", false);

pref("gfx.font_rendering.graphite.enabled", true);

// Check intl/unicharutil/util/nsUnicodeProperties.h for definitions of script bits
// in the ShapingType enumeration
// Currently-defined bits:
//  SHAPING_DEFAULT   = 0x0001,
//  SHAPING_ARABIC    = 0x0002,
//  SHAPING_HEBREW    = 0x0004,
//  SHAPING_HANGUL    = 0x0008,
//  SHAPING_MONGOLIAN = 0x0010,
//  SHAPING_INDIC     = 0x0020,
//  SHAPING_THAI      = 0x0040
// (see http://mxr.mozilla.org/mozilla-central/ident?i=ShapingType)
// Scripts not listed are grouped in the default category.
// Set the pref to -1 to have all text shaped via the harfbuzz backend.
//@line 291 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
// use harfbuzz for all scripts (except when using AAT fonts on OS X)
pref("gfx.font_rendering.harfbuzz.scripts", -1);
//@line 294 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 299 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

pref("gfx.font_rendering.opentype_svg.enabled", false);

//@line 309 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("gfx.content.azure.enabled", false);
//@line 315 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("gfx.canvas.azure.backends", "cairo");
pref("gfx.content.azure.backends", "cairo");
//@line 319 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 323 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

pref("gfx.work-around-driver-bugs", true);
pref("gfx.prefer-mesa-llvmpipe", false);

pref("accessibility.browsewithcaret", false);
pref("accessibility.warn_on_browsewithcaret", true);

pref("accessibility.browsewithcaret_shortcut.enabled", true);

//@line 333 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
// Tab focus model bit field:
// 1 focuses text controls, 2 focuses other form elements, 4 adds links.
// Most users will want 1, 3, or 7.
// On OS X, we use Full Keyboard Access system preference,
// unless accessibility.tabfocus is set by the user.
pref("accessibility.tabfocus", 7);
pref("accessibility.tabfocus_applies_to_xul", false);

// On OS X, we follow the "Click in the scrollbar to:" system preference
// unless this preference was set manually
pref("ui.scrollToClick", 0);

//@line 349 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// We want the ability to forcibly disable platform a11y, because
// some non-a11y-related components attempt to bring it up.  See bug
// 538530 for details about Windows; we have a pref here that allows it
// to be disabled for performance and testing resons.
// See bug 761589 for the crossplatform aspect.
//
// This pref is checked only once, and the browser needs a restart to
// pick up any changes.
//
// Values are -1 always on. 1 always off, 0 is auto as some platform perform
// further checks.
pref("accessibility.force_disabled", 0);

//@line 372 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

pref("focusmanager.testmode", false);

pref("accessibility.usetexttospeech", "");
pref("accessibility.usebrailledisplay", "");
pref("accessibility.accesskeycausesactivation", true);
pref("accessibility.mouse_focuses_formcontrol", false);

// Type Ahead Find
pref("accessibility.typeaheadfind", true);
pref("accessibility.typeaheadfind.autostart", true);
// casesensitive: controls the find bar's case-sensitivity
//     0 - "never"  (case-insensitive)
//     1 - "always" (case-sensitive)
// other - "auto"   (case-sensitive for mixed-case input, insensitive otherwise)
pref("accessibility.typeaheadfind.casesensitive", 0);
pref("accessibility.typeaheadfind.linksonly", true);
pref("accessibility.typeaheadfind.startlinksonly", false);
pref("accessibility.typeaheadfind.timeout", 4000);
pref("accessibility.typeaheadfind.enabletimeout", true);
pref("accessibility.typeaheadfind.soundURL", "beep");
pref("accessibility.typeaheadfind.enablesound", true);
pref("accessibility.typeaheadfind.prefillwithselection", true);

// use Mac OS X Appearance panel text smoothing setting when rendering text, disabled by default
pref("gfx.use_text_smoothing_setting", false);

// loading and rendering of framesets and iframes
pref("browser.frames.enabled", true);

// Number of characters to consider emphasizing for rich autocomplete results
pref("toolkit.autocomplete.richBoundaryCutoff", 200);

// Variable controlling logging for osfile.
pref("toolkit.osfile.log", false);

pref("toolkit.scrollbox.smoothScroll", true);
pref("toolkit.scrollbox.scrollIncrement", 20);
pref("toolkit.scrollbox.verticalScrollDistance", 3);
pref("toolkit.scrollbox.horizontalScrollDistance", 5);
pref("toolkit.scrollbox.clickToScroll.scrollDelay", 150);

// Telemetry
//@line 418 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("toolkit.telemetry.enabled", false);
//@line 420 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("toolkit.telemetry.server", "https://data.mozilla.com");
// Telemetry server owner. Please change if you set toolkit.telemetry.server to a different server
pref("toolkit.telemetry.server_owner", "Mozilla");
// Information page about telemetry (temporary ; will be about:telemetry in the end)
pref("toolkit.telemetry.infoURL", "https://www.mozilla.org/legal/privacy/firefox.html#telemetry");
// Determines whether full SQL strings are returned when they might contain sensitive info
// i.e. dynamically constructed SQL strings or SQL executed by addons against addon DBs
pref("toolkit.telemetry.debugSlowSql", false);

// Identity module
pref("toolkit.identity.enabled", false);
pref("toolkit.identity.debug", false);

// Enable deprecation warnings.
pref("devtools.errorconsole.deprecation_warnings", true);

// Disable remote debugging protocol logging
pref("devtools.debugger.log", false);
// Disable remote debugging connections
pref("devtools.debugger.remote-enabled", false);
pref("devtools.debugger.remote-port", 6000);
// Force debugger server binding on the loopback interface
pref("devtools.debugger.force-local", true);

// view source
pref("view_source.syntax_highlight", true);
pref("view_source.wrap_long_lines", false);
pref("view_source.editor.external", false);
pref("view_source.editor.path", "");
// allows to add further arguments to the editor; use the %LINE% placeholder
// for jumping to a specific line (e.g. "/line:%LINE%" or "--goto %LINE%")
pref("view_source.editor.args", "");

// When true this will word-wrap plain text documents.
pref("plain_text.wrap_long_lines", false);

// dispatch left clicks only to content in browser (still allows clicks to chrome/xul)
pref("nglayout.events.dispatchLeftClickOnly", true);

// whether or not to draw images while dragging
pref("nglayout.enable_drag_images", true);

// enable/disable paint flashing --- useful for debugging
pref("nglayout.debug.paint_flashing", false);

// enable/disable widget update area flashing --- only supported with 
// BasicLayers (other layer managers always update the entire widget area)
pref("nglayout.debug.widget_update_flashing", false);

// scrollbar snapping region
// 0 - off
// 1 and higher - slider thickness multiple
pref("slider.snapMultiplier", 0);

// option to choose plug-in finder
pref("application.use_ns_plugin_finder", false);

// URI fixup prefs
pref("browser.fixup.alternate.enabled", true);
pref("browser.fixup.alternate.prefix", "www.");
pref("browser.fixup.alternate.suffix", ".com");
pref("browser.fixup.hide_user_pass", true);
pref("browser.fixup.use-utf8", false);

// Location Bar AutoComplete
pref("browser.urlbar.autocomplete.enabled", true);

// Print header customization
// Use the following codes:
// &T - Title
// &U - Document URL
// &D - Date/Time
// &P - Page Number
// &PT - Page Number "of" Page total
// Set each header to a string containing zero or one of these codes
// and the code will be replaced in that string by the corresponding data
pref("print.print_headerleft", "&T");
pref("print.print_headercenter", "");
pref("print.print_headerright", "&U");
pref("print.print_footerleft", "&PT");
pref("print.print_footercenter", "");
pref("print.print_footerright", "&D");
pref("print.show_print_progress", true);

// xxxbsmedberg: more toolkit prefs

// When this is set to false each window has its own PrintSettings
// and a change in one window does not affect the others
pref("print.use_global_printsettings", true);

// Save the Printings after each print job
pref("print.save_print_settings", true);

pref("print.whileInPrintPreview", true);

// Cache old Presentation when going into Print Preview
pref("print.always_cache_old_pres", false);

// Enables you to specify the amount of the paper that is to be treated
// as unwriteable.  The print_edge_XXX and print_margin_XXX preferences
// are treated as offsets that are added to this pref.
// Default is "-1", which means "use the system default".  (If there is
// no system default, then the -1 is treated as if it were 0.)
// This is used by both Printing and Print Preview.
// Units are in 1/100ths of an inch.
pref("print.print_unwriteable_margin_top",    -1);
pref("print.print_unwriteable_margin_left",   -1);
pref("print.print_unwriteable_margin_right",  -1);
pref("print.print_unwriteable_margin_bottom", -1);

// Enables you to specify the gap from the edge of the paper's 
// unwriteable area to the margin.
// This is used by both Printing and Print Preview
// Units are in 1/100ths of an inch.
pref("print.print_edge_top", 0);
pref("print.print_edge_left", 0);
pref("print.print_edge_right", 0);
pref("print.print_edge_bottom", 0);

// Pref used by the spellchecker extension to control the 
// maximum number of misspelled words that will be underlined
// in a document.
pref("extensions.spellcheck.inline.max-misspellings", 500);

// Prefs used by libeditor. Prefs specific to seamonkey composer
// belong in comm-central/editor/ui/composer.js

pref("editor.use_custom_colors", false);
pref("editor.singleLine.pasteNewlines",      2);
pref("editor.use_css",                       false);
pref("editor.css.default_length_unit",       "px");
pref("editor.resizing.preserve_ratio",       true);
pref("editor.positioning.offset",            0);


// Default Capability Preferences: Security-Critical! 
// Editing these may create a security risk - be sure you know what you're doing
//pref("capability.policy.default.barprop.visible.set", "UniversalXPConnect");

pref("capability.policy.default_policynames", "mailnews");

pref("capability.policy.default.DOMException.code", "allAccess");
pref("capability.policy.default.DOMException.message", "allAccess");
pref("capability.policy.default.DOMException.name", "allAccess");
pref("capability.policy.default.DOMException.result", "allAccess");
pref("capability.policy.default.DOMException.toString.get", "allAccess");

pref("capability.policy.default.History.back.get", "allAccess");
pref("capability.policy.default.History.current", "UniversalXPConnect");
pref("capability.policy.default.History.forward.get", "allAccess");
pref("capability.policy.default.History.go.get", "allAccess");
pref("capability.policy.default.History.item", "UniversalXPConnect");
pref("capability.policy.default.History.next", "UniversalXPConnect");
pref("capability.policy.default.History.previous", "UniversalXPConnect");
pref("capability.policy.default.History.toString", "UniversalXPConnect");

pref("capability.policy.default.Location.hash.set", "allAccess");
pref("capability.policy.default.Location.href.set", "allAccess");
pref("capability.policy.default.Location.replace.get", "allAccess");

pref("capability.policy.default.Window.blur.get", "allAccess");
pref("capability.policy.default.Window.close.get", "allAccess");
pref("capability.policy.default.Window.closed.get", "allAccess");
pref("capability.policy.default.Window.focus.get", "allAccess");
pref("capability.policy.default.Window.frames.get", "allAccess");
pref("capability.policy.default.Window.history.get", "allAccess");
pref("capability.policy.default.Window.length.get", "allAccess");
pref("capability.policy.default.Window.location", "allAccess");
pref("capability.policy.default.Window.opener.get", "allAccess");
pref("capability.policy.default.Window.parent.get", "allAccess");
pref("capability.policy.default.Window.postMessage.get", "allAccess");
pref("capability.policy.default.Window.self.get", "allAccess");
pref("capability.policy.default.Window.top.get", "allAccess");
pref("capability.policy.default.Window.window.get", "allAccess");

pref("capability.policy.default.Selection.addSelectionListener", "UniversalXPConnect");
pref("capability.policy.default.Selection.removeSelectionListener", "UniversalXPConnect");

// Restrictions on the DOM for mail/news - see bugs 66938 and 84545
pref("capability.policy.mailnews.sites", "mailbox: imap: news:");

pref("capability.policy.mailnews.*.attributes.get", "noAccess");
pref("capability.policy.mailnews.*.baseURI.get", "noAccess");
pref("capability.policy.mailnews.*.data.get", "noAccess");
pref("capability.policy.mailnews.*.getAttribute", "noAccess");
pref("capability.policy.mailnews.HTMLDivElement.getAttribute", "sameOrigin");
pref("capability.policy.mailnews.*.getAttributeNS", "noAccess");
pref("capability.policy.mailnews.*.getAttributeNode", "noAccess");
pref("capability.policy.mailnews.*.getAttributeNodeNS", "noAccess");
pref("capability.policy.mailnews.*.getNamedItem", "noAccess");
pref("capability.policy.mailnews.*.getNamedItemNS", "noAccess");
pref("capability.policy.mailnews.*.host.get", "noAccess");
pref("capability.policy.mailnews.*.hostname.get", "noAccess");
pref("capability.policy.mailnews.*.href.get", "noAccess");
pref("capability.policy.mailnews.*.innerHTML.get", "noAccess");
pref("capability.policy.mailnews.*.lowSrc.get", "noAccess");
pref("capability.policy.mailnews.*.nodeValue.get", "noAccess");
pref("capability.policy.mailnews.*.pathname.get", "noAccess");
pref("capability.policy.mailnews.*.protocol.get", "noAccess");
pref("capability.policy.mailnews.*.src.get", "noAccess");
pref("capability.policy.mailnews.*.substringData.get", "noAccess");
pref("capability.policy.mailnews.*.text.get", "noAccess");
pref("capability.policy.mailnews.*.textContent", "noAccess");
pref("capability.policy.mailnews.*.title.get", "noAccess");
pref("capability.policy.mailnews.*.wholeText", "noAccess");
pref("capability.policy.mailnews.DOMException.toString", "noAccess");
pref("capability.policy.mailnews.HTMLAnchorElement.toString", "noAccess");
pref("capability.policy.mailnews.HTMLDocument.domain", "noAccess");
pref("capability.policy.mailnews.HTMLDocument.URL", "noAccess");
pref("capability.policy.mailnews.*.documentURI", "noAccess");
pref("capability.policy.mailnews.Location.toString", "noAccess");
pref("capability.policy.mailnews.Range.toString", "noAccess");
pref("capability.policy.mailnews.Window.blur", "noAccess");
pref("capability.policy.mailnews.Window.focus", "noAccess");
pref("capability.policy.mailnews.Window.innerWidth.set", "noAccess");
pref("capability.policy.mailnews.Window.innerHeight.set", "noAccess");
pref("capability.policy.mailnews.Window.moveBy", "noAccess");
pref("capability.policy.mailnews.Window.moveTo", "noAccess");
pref("capability.policy.mailnews.Window.name.set", "noAccess");
pref("capability.policy.mailnews.Window.outerHeight.set", "noAccess");
pref("capability.policy.mailnews.Window.outerWidth.set", "noAccess");
pref("capability.policy.mailnews.Window.resizeBy", "noAccess");
pref("capability.policy.mailnews.Window.resizeTo", "noAccess");
pref("capability.policy.mailnews.Window.screenX.set", "noAccess");
pref("capability.policy.mailnews.Window.screenY.set", "noAccess");
pref("capability.policy.mailnews.Window.sizeToContent", "noAccess");
pref("capability.policy.mailnews.document.load", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.channel", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.getInterface", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.responseXML", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.responseText", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.status", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.statusText", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.abort", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.getAllResponseHeaders", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.getResponseHeader", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.open", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.send", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.setRequestHeader", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.readyState", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.overrideMimeType", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.onload", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.onerror", "noAccess");
pref("capability.policy.mailnews.XMLHttpRequest.onreadystatechange", "noAccess");
pref("capability.policy.mailnews.XMLSerializer.serializeToString", "noAccess");
pref("capability.policy.mailnews.XMLSerializer.serializeToStream", "noAccess");
pref("capability.policy.mailnews.DOMParser.parseFromString", "noAccess");
pref("capability.policy.mailnews.DOMParser.parseFromStream", "noAccess");
pref("capability.policy.mailnews.SOAPCall.transportURI", "noAccess");
pref("capability.policy.mailnews.SOAPCall.verifySourceHeader", "noAccess");
pref("capability.policy.mailnews.SOAPCall.invoke", "noAccess");
pref("capability.policy.mailnews.SOAPCall.asyncInvoke", "noAccess");
pref("capability.policy.mailnews.SOAPResponse.fault", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.styleURI", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.getAssociatedEncoding", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.setEncoder", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.getEncoder", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.setDecoder", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.setDecoder", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.getDecoder", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.defaultEncoder", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.defaultDecoder", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.schemaCollection", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.encode", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.decode", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.mapSchemaURI", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.unmapSchemaURI", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.getInternalSchemaURI", "noAccess");
pref("capability.policy.mailnews.SOAPEncoding.getExternalSchemaURI", "noAccess");
pref("capability.policy.mailnews.SOAPFault.element", "noAccess");
pref("capability.policy.mailnews.SOAPFault.faultNamespaceURI", "noAccess");
pref("capability.policy.mailnews.SOAPFault.faultCode", "noAccess");
pref("capability.policy.mailnews.SOAPFault.faultString", "noAccess");
pref("capability.policy.mailnews.SOAPFault.faultActor", "noAccess");
pref("capability.policy.mailnews.SOAPFault.detail", "noAccess");
pref("capability.policy.mailnews.SOAPHeaderBlock.actorURI", "noAccess");
pref("capability.policy.mailnews.SOAPHeaderBlock.mustUnderstand", "noAccess");
pref("capability.policy.mailnews.SOAPParameter", "noAccess");
pref("capability.policy.mailnews.SOAPPropertyBagMutator.propertyBag", "noAccess");
pref("capability.policy.mailnews.SOAPPropertyBagMutator.addProperty", "noAccess");
pref("capability.policy.mailnews.SchemaLoader.load", "noAccess");
pref("capability.policy.mailnews.SchemaLoader.loadAsync", "noAccess");
pref("capability.policy.mailnews.SchemaLoader.processSchemaElement", "noAccess");
pref("capability.policy.mailnews.SchemaLoader.onLoad", "noAccess");
pref("capability.policy.mailnews.SchemaLoader.onError", "noAccess");
pref("capability.policy.mailnews.WSDLLoader.load", "noAccess");
pref("capability.policy.mailnews.WSDLLoader.loadAsync", "noAccess");
pref("capability.policy.mailnews.WSDLLoader.onLoad", "noAccess");
pref("capability.policy.mailnews.WSDLLoader.onError", "noAccess");
pref("capability.policy.mailnews.WebServiceProxyFactory.createProxy", "noAccess");
pref("capability.policy.mailnews.WebServiceProxyFactory.createProxyAsync", "noAccess");
pref("capability.policy.mailnews.WebServiceProxyFactory.onLoad", "noAccess");
pref("capability.policy.mailnews.WebServiceProxyFactory.onError", "noAccess");

// XMLExtras
pref("capability.policy.default.XMLHttpRequest.channel", "noAccess");
pref("capability.policy.default.XMLHttpRequest.getInterface", "noAccess");
pref("capability.policy.default.XMLHttpRequest.open-uri", "allAccess");
pref("capability.policy.default.DOMParser.parseFromStream", "noAccess");

// Clipboard
pref("capability.policy.default.Clipboard.cutcopy", "noAccess");
pref("capability.policy.default.Clipboard.paste", "noAccess");

// Scripts & Windows prefs
pref("dom.disable_image_src_set",           false);
pref("dom.disable_window_flip",             false);
pref("dom.disable_window_move_resize",      false);
pref("dom.disable_window_status_change",    false);

pref("dom.disable_window_open_feature.titlebar",    false);
pref("dom.disable_window_open_feature.close",       false);
pref("dom.disable_window_open_feature.toolbar",     false);
pref("dom.disable_window_open_feature.location",    false);
pref("dom.disable_window_open_feature.personalbar", false);
pref("dom.disable_window_open_feature.menubar",     false);
pref("dom.disable_window_open_feature.scrollbars",  false);
pref("dom.disable_window_open_feature.resizable",   true);
pref("dom.disable_window_open_feature.minimizable", false);
pref("dom.disable_window_open_feature.status",      true);

pref("dom.allow_scripts_to_close_windows",          false);

pref("dom.disable_open_during_load",                false);
pref("dom.popup_maximum",                           20);
pref("dom.popup_allowed_events", "change click dblclick mouseup reset submit touchend");
pref("dom.disable_open_click_delay", 1000);

pref("dom.storage.enabled", true);
pref("dom.storage.default_quota",      5120);

pref("dom.send_after_paint_to_content", false);

// Timeout clamp in ms for timeouts we clamp
pref("dom.min_timeout_value", 4);
// And for background windows
pref("dom.min_background_timeout_value", 1000);

// Stop defining the Components object in content.
pref("dom.omit_components_in_content", true);

// Don't use new input types
pref("dom.experimental_forms", false);

// Don't enable <input type=range> yet:
pref("dom.experimental_forms_range", true);

// Don't enable <input type=color> yet:
pref("dom.forms.color", false);

// Enables system messages and activities
pref("dom.sysmsg.enabled", false);

// Parsing perf prefs. For now just mimic what the old code did.
//@line 775 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("content.sink.pending_event_mode", 0);
//@line 777 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Disable popups from plugins by default
//   0 = openAllowed
//   1 = openControlled
//   2 = openAbused
pref("privacy.popups.disable_from_plugins", 2);

// "do not track" HTTP header, disabled by default
pref("privacy.donottrackheader.enabled",    false);
//   0 = tracking is acceptable
//   1 = tracking is unacceptable
pref("privacy.donottrackheader.value",      1);

pref("dom.event.contextmenu.enabled",       true);
pref("dom.event.clipboardevents.enabled",   true);

pref("javascript.enabled",                  true);
pref("javascript.options.strict",           false);
//@line 798 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("javascript.options.baselinejit.content", true);
pref("javascript.options.baselinejit.chrome",  true);
pref("javascript.options.ion.content",      true);
pref("javascript.options.asmjs",            true);
pref("javascript.options.ion.parallel_compilation", true);
pref("javascript.options.pccounts.content", false);
pref("javascript.options.pccounts.chrome",  false);
pref("javascript.options.jit_hardening", true);
pref("javascript.options.typeinference", true);
// This preference limits the memory usage of javascript.
// If you want to change these values for your device,
// please find Bug 417052 comment 17 and Bug 456721
// Comment 32 and Bug 613551.
pref("javascript.options.mem.high_water_mark", 128);
pref("javascript.options.mem.max", -1);
pref("javascript.options.mem.gc_per_compartment", true);
pref("javascript.options.mem.disable_explicit_compartment_gc", true);
pref("javascript.options.mem.gc_incremental", true);
pref("javascript.options.mem.gc_incremental_slice_ms", 10);
pref("javascript.options.mem.log", false);
pref("javascript.options.mem.notify", false);
pref("javascript.options.gc_on_memory_pressure", true);

pref("javascript.options.mem.gc_high_frequency_time_limit_ms", 1000);
pref("javascript.options.mem.gc_high_frequency_low_limit_mb", 100);
pref("javascript.options.mem.gc_high_frequency_high_limit_mb", 500);
pref("javascript.options.mem.gc_high_frequency_heap_growth_max", 300);
pref("javascript.options.mem.gc_high_frequency_heap_growth_min", 150);
pref("javascript.options.mem.gc_low_frequency_heap_growth", 150);
pref("javascript.options.mem.gc_dynamic_heap_growth", true);
pref("javascript.options.mem.gc_dynamic_mark_slice", true);
pref("javascript.options.mem.gc_allocation_threshold_mb", 30);
pref("javascript.options.mem.gc_decommit_threshold_mb", 32);

pref("javascript.options.mem.analysis_purge_mb", 100);

pref("javascript.options.showInConsole", false);

// advanced prefs
pref("advanced.mailftp",                    false);
pref("image.animation_mode",                "normal");

// Same-origin policy for file URIs, "false" is traditional
pref("security.fileuri.strict_origin_policy", true);

// If there is ever a security firedrill that requires
// us to block certian ports global, this is the pref 
// to use.  Is is a comma delimited list of port numbers
// for example:
//   pref("network.security.ports.banned", "1,2,3,4,5");
// prevents necko connecting to ports 1-5 unless the protocol
// overrides.

// Allow necko to do A/B testing. Will generally only happen if
// telemetry is also enabled as otherwise there is no way to report
// the results
pref("network.allow-experiments", true);

// Turn off interprocess security checks. Needed to run xpcshell tests.
pref("network.disable.ipc.security", false);

// Default action for unlisted external protocol handlers
pref("network.protocol-handler.external-default", true);      // OK to load
pref("network.protocol-handler.warn-external-default", true); // warn before load

// Prevent using external protocol handlers for these schemes
pref("network.protocol-handler.external.hcp", false);
pref("network.protocol-handler.external.vbscript", false);
pref("network.protocol-handler.external.javascript", false);
pref("network.protocol-handler.external.data", false);
pref("network.protocol-handler.external.ms-help", false);
pref("network.protocol-handler.external.shell", false);
pref("network.protocol-handler.external.vnd.ms.radio", false);
//@line 874 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("network.protocol-handler.external.disk", false);
pref("network.protocol-handler.external.disks", false);
pref("network.protocol-handler.external.afp", false);
pref("network.protocol-handler.external.moz-icon", false);

// An exposed protocol handler is one that can be used in all contexts.  A
// non-exposed protocol handler is one that can only be used internally by the
// application.  For example, a non-exposed protocol would not be loaded by the
// application in response to a link click or a X-remote openURL command.
// Instead, it would be deferred to the system's external protocol handler.
// Only internal/built-in protocol handlers can be marked as exposed.

// This pref controls the default settings.  Per protocol settings can be used
// to override this value.
pref("network.protocol-handler.expose-all", true);

// Example: make IMAP an exposed protocol
// pref("network.protocol-handler.expose.imap", true);

// <http>
pref("network.http.version", "1.1");	  // default
// pref("network.http.version", "1.0");   // uncomment this out in case of problems
// pref("network.http.version", "0.9");   // it'll work too if you're crazy
// keep-alive option is effectively obsolete. Nevertheless it'll work with
// some older 1.0 servers:

pref("network.http.proxy.version", "1.1");    // default
// pref("network.http.proxy.version", "1.0"); // uncomment this out in case of problems
                                              // (required if using junkbuster proxy)

// enable caching of http documents
pref("network.http.use-cache", true);

// this preference can be set to override the socket type used for normal
// HTTP traffic.  an empty value indicates the normal TCP/IP socket type.
pref("network.http.default-socket-type", "");

// There is a problem with some IIS7 servers that don't close the connection
// properly after it times out (bug #491541). Default timeout on IIS7 is
// 120 seconds. We need to reuse or drop the connection within this time.
// We set the timeout a little shorter to keep a reserve for cases when
// the packet is lost or delayed on the route.
pref("network.http.keep-alive.timeout", 115);

// Limit the absolute number of http connections.
// Note: the socket transport service will clamp the number below 256 if the OS
// cannot allocate that many FDs, and it also always tries to reserve up to 250
// file descriptors for things other than sockets.   
pref("network.http.max-connections", 256);

// If NOT connecting via a proxy, then
// a new connection will only be attempted if the number of active persistent
// connections to the server is less then max-persistent-connections-per-server.
pref("network.http.max-persistent-connections-per-server", 6);

// If connecting via a proxy, then a
// new connection will only be attempted if the number of active persistent
// connections to the proxy is less then max-persistent-connections-per-proxy.
pref("network.http.max-persistent-connections-per-proxy", 32);

// amount of time (in seconds) to suspend pending requests, before spawning a
// new connection, once the limit on the number of persistent connections per
// host has been reached.  however, a new connection will not be created if
// max-connections or max-connections-per-server has also been reached.
pref("network.http.request.max-start-delay", 10);

// Headers
pref("network.http.accept.default", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");
pref("network.http.sendRefererHeader",      2); // 0=don't send any, 1=send only on clicks, 2=send on image requests as well

// Controls whether we send HTTPS referres to other HTTPS sites.
// By default this is enabled for compatibility (see bug 141641)
pref("network.http.sendSecureXSiteReferrer", true);

// Maximum number of consecutive redirects before aborting.
pref("network.http.redirection-limit", 20);

// Enable http compression: comment this out in case of problems with 1.1
// NOTE: support for "compress" has been disabled per bug 196406.
// NOTE: separate values with comma+space (", "): see bug 576033
pref("network.http.accept-encoding", "gzip, deflate");

pref("network.http.pipelining"      , false);
pref("network.http.pipelining.ssl"  , false); // disable pipelining over SSL
pref("network.http.pipelining.abtest", false);
pref("network.http.proxy.pipelining", false);

// Max number of requests in the pipeline
pref("network.http.pipelining.maxrequests" , 32);

// An optimistic request is one pipelined when policy might allow a new
// connection instead
pref("network.http.pipelining.max-optimistic-requests" , 4);

pref("network.http.pipelining.aggressive", false);
pref("network.http.pipelining.maxsize" , 300000);
pref("network.http.pipelining.reschedule-on-timeout", true);
pref("network.http.pipelining.reschedule-timeout", 1500);

// The read-timeout is a ms timer that causes the transaction to be completely
// restarted without pipelining.
pref("network.http.pipelining.read-timeout", 30000);

// Prompt for 307 redirects
pref("network.http.prompt-temp-redirect", true);

// If true generate CORRUPTED_CONTENT errors for entities that
// contain an invalid Assoc-Req response header
pref("network.http.assoc-req.enforce", false);

// On networks deploying QoS, it is recommended that these be lockpref()'d,
// since inappropriate marking can easily overwhelm bandwidth reservations
// for certain services (i.e. EF for VoIP, AF4x for interactive video,
// AF3x for broadcast/streaming video, etc)

// default value for HTTP
// in a DSCP environment this should be 40 (0x28, or AF11), per RFC-4594,
// Section 4.8 "High-Throughput Data Service Class"
pref("network.http.qos", 0);

// The number of milliseconds after sending a SYN for an HTTP connection,
// to wait before trying a different connection. 0 means do not use a second
// connection.
pref("network.http.connection-retry-timeout", 250);

// The number of seconds after sending initial SYN for an HTTP connection
// to give up if the OS does not give up first
pref("network.http.connection-timeout", 90);

// The maximum number of current global half open sockets allowable
// when starting a new speculative connection.
pref("network.http.speculative-parallel-limit", 6);

// Whether or not to block requests for non head js/css items (e.g. media)
// while those elements load.
pref("network.http.rendering-critical-requests-prioritization", true);

// Disable IPv6 for backup connections to workaround problems about broken
// IPv6 connectivity.
pref("network.http.fast-fallback-to-IPv4", true);

// The maximum amount of time the cache session lock can be held
// before a new transaction bypasses the cache. In milliseconds.
//@line 1018 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("network.http.bypass-cachelock-threshold", 200000);
//@line 1022 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Try and use SPDY when using SSL
pref("network.http.spdy.enabled", true);
pref("network.http.spdy.enabled.v2", true);
pref("network.http.spdy.enabled.v3", true);
pref("network.http.spdy.chunk-size", 4096);
pref("network.http.spdy.timeout", 180);
pref("network.http.spdy.coalesce-hostnames", true);
pref("network.http.spdy.persistent-settings", false);
pref("network.http.spdy.ping-threshold", 58);
pref("network.http.spdy.ping-timeout", 8);
pref("network.http.spdy.send-buffer-size", 131072);
pref("network.http.spdy.allow-push", true);
pref("network.http.spdy.push-allowance", 65536);

pref("network.http.diagnostics", false);

pref("network.http.pacing.requests.enabled", true);
pref("network.http.pacing.requests.min-parallelism", 6);
pref("network.http.pacing.requests.hz", 100);
pref("network.http.pacing.requests.burst", 32);

// default values for FTP
// in a DSCP environment this should be 40 (0x28, or AF11), per RFC-4594,
// Section 4.8 "High-Throughput Data Service Class", and 80 (0x50, or AF22)
// per Section 4.7 "Low-Latency Data Service Class".
pref("network.ftp.data.qos", 0);
pref("network.ftp.control.qos", 0);

// </http>

// <ws>: WebSocket
pref("network.websocket.enabled", true);

// 2147483647 == PR_INT32_MAX == ~2 GB  
pref("network.websocket.max-message-size", 2147483647);

// Should we automatically follow http 3xx redirects during handshake
pref("network.websocket.auto-follow-http-redirects", false);

// the number of seconds to wait for websocket connection to be opened
pref("network.websocket.timeout.open", 20);

// the number of seconds to wait for a clean close after sending the client
// close message
pref("network.websocket.timeout.close", 20);

// the number of seconds of idle read activity to sustain before sending a
// ping probe. 0 to disable.
pref("network.websocket.timeout.ping.request", 0);

// the deadline, expressed in seconds, for some read activity to occur after
// generating a ping. If no activity happens then an error and unclean close
// event is sent to the javascript websockets application
pref("network.websocket.timeout.ping.response", 10);

// Defines whether or not to try and negotiate the stream-deflate compression
// extension with the websocket server. Stream-Deflate has been removed from
// the standards track document, but can still be used by servers who opt
// into it.
pref("network.websocket.extensions.stream-deflate", false);

// the maximum number of concurrent websocket sessions. By specification there
// is never more than one handshake oustanding to an individual host at
// one time.
pref("network.websocket.max-connections", 200);

// by default scripts loaded from a https:// origin can only open secure
// (i.e. wss://) websockets.
pref("network.websocket.allowInsecureFromHTTPS", false);

// by default we delay websocket reconnects to same host/port if previous
// connection failed, per RFC 6455 section 7.2.3 
pref("network.websocket.delay-failed-reconnects", true);

// </ws>

// Server-Sent Events

pref("dom.server-events.enabled", true);
// Equal to the DEFAULT_RECONNECTION_TIME_VALUE value in nsEventSource.cpp
pref("dom.server-events.default-reconnection-time", 5000); // in milliseconds

// If false, remote JAR files that are served with a content type other than
// application/java-archive or application/x-jar will not be opened
// by the jar channel.
pref("network.jar.open-unsafe-types", false);

// This preference, if true, causes all UTF-8 domain names to be normalized to
// punycode.  The intention is to allow UTF-8 domain names as input, but never
// generate them from punycode.
pref("network.IDN_show_punycode", false);

// If "network.IDN.use_whitelist" is set to true, TLDs with
// "network.IDN.whitelist.tld" explicitly set to true are treated as
// IDN-safe. Otherwise, they're treated as unsafe and punycode will be used
// for displaying them in the UI (e.g. URL bar), unless they conform to one of
// the profiles specified in
// http://www.unicode.org/reports/tr36/proposed.html#Security_Levels_and_Alerts
// If "network.IDN.restriction_profile" is "high", the Highly Restrictive
// profile is used.
// If "network.IDN.restriction_profile" is "moderate", the Moderately
// Restrictive profile is used.
// In all other cases, the ASCII-Only profile is used.
// Note that these preferences are referred to ONLY when
// "network.IDN_show_punycode" is false. In other words, all IDNs will be shown
// in punycode if "network.IDN_show_punycode" is true.
pref("network.IDN.restriction_profile", "moderate");
pref("network.IDN.use_whitelist", true);

// ccTLDs
pref("network.IDN.whitelist.ac", true);
pref("network.IDN.whitelist.ar", true);
pref("network.IDN.whitelist.at", true);
pref("network.IDN.whitelist.br", true);
pref("network.IDN.whitelist.ca", true);
pref("network.IDN.whitelist.ch", true);
pref("network.IDN.whitelist.cl", true);
pref("network.IDN.whitelist.cn", true);
pref("network.IDN.whitelist.de", true);
pref("network.IDN.whitelist.dk", true);
pref("network.IDN.whitelist.ee", true);
pref("network.IDN.whitelist.es", true);
pref("network.IDN.whitelist.fi", true);
pref("network.IDN.whitelist.fr", true);
pref("network.IDN.whitelist.gr", true);
pref("network.IDN.whitelist.gt", true);
pref("network.IDN.whitelist.hu", true);
pref("network.IDN.whitelist.il", true);
pref("network.IDN.whitelist.io", true);
pref("network.IDN.whitelist.ir", true);
pref("network.IDN.whitelist.is", true);
pref("network.IDN.whitelist.jp", true);
pref("network.IDN.whitelist.kr", true);
pref("network.IDN.whitelist.li", true);
pref("network.IDN.whitelist.lt", true);
pref("network.IDN.whitelist.lu", true);
pref("network.IDN.whitelist.lv", true);
pref("network.IDN.whitelist.no", true);
pref("network.IDN.whitelist.nu", true);
pref("network.IDN.whitelist.nz", true);
pref("network.IDN.whitelist.pl", true);
pref("network.IDN.whitelist.pm", true);
pref("network.IDN.whitelist.pr", true);
pref("network.IDN.whitelist.re", true);
pref("network.IDN.whitelist.se", true);
pref("network.IDN.whitelist.sh", true);
pref("network.IDN.whitelist.si", true);
pref("network.IDN.whitelist.tf", true);
pref("network.IDN.whitelist.th", true);
pref("network.IDN.whitelist.tm", true);
pref("network.IDN.whitelist.tw", true);
pref("network.IDN.whitelist.ua", true);
pref("network.IDN.whitelist.vn", true);
pref("network.IDN.whitelist.wf", true);
pref("network.IDN.whitelist.yt", true);

// IDN ccTLDs
// ae, UAE, .<Emarat>
pref("network.IDN.whitelist.xn--mgbaam7a8h", true); 
// cn, China, .<China> with variants
pref("network.IDN.whitelist.xn--fiqz9s", true); // Traditional
pref("network.IDN.whitelist.xn--fiqs8s", true); // Simplified
// eg, Egypt, .<Masr>
pref("network.IDN.whitelist.xn--wgbh1c", true);
// hk, Hong Kong, .<Hong Kong>
pref("network.IDN.whitelist.xn--j6w193g", true);
// ir, Iran, <.Iran> with variants
pref("network.IDN.whitelist.xn--mgba3a4f16a", true);
pref("network.IDN.whitelist.xn--mgba3a4fra", true);
// jo, Jordan, .<Al-Ordon>
pref("network.IDN.whitelist.xn--mgbayh7gpa", true);
// lk, Sri Lanka, .<Lanka> and .<Ilangai>
pref("network.IDN.whitelist.xn--fzc2c9e2c", true);
pref("network.IDN.whitelist.xn--xkc2al3hye2a", true);
// qa, Qatar, .<Qatar>
pref("network.IDN.whitelist.xn--wgbl6a", true);
// rs, Serbia, .<Srb>
pref("network.IDN.whitelist.xn--90a3ac", true);
// ru, Russian Federation, .<RF>
pref("network.IDN.whitelist.xn--p1ai", true);
// sa, Saudi Arabia, .<al-Saudiah> with variants
pref("network.IDN.whitelist.xn--mgberp4a5d4ar", true); 
pref("network.IDN.whitelist.xn--mgberp4a5d4a87g", true);
pref("network.IDN.whitelist.xn--mgbqly7c0a67fbc", true);
pref("network.IDN.whitelist.xn--mgbqly7cvafr", true);
// sy, Syria, .<Souria>
pref("network.IDN.whitelist.xn--ogbpf8fl", true);
// th, Thailand, .<Thai>
pref("network.IDN.whitelist.xn--o3cw4h", true);
// tw, Taiwan, <.Taiwan> with variants
pref("network.IDN.whitelist.xn--kpry57d", true);  // Traditional
pref("network.IDN.whitelist.xn--kprw13d", true);  // Simplified

// gTLDs
pref("network.IDN.whitelist.asia", true);
pref("network.IDN.whitelist.biz", true);
pref("network.IDN.whitelist.cat", true);
pref("network.IDN.whitelist.info", true);
pref("network.IDN.whitelist.museum", true);
pref("network.IDN.whitelist.org", true);
pref("network.IDN.whitelist.tel", true);

// NOTE: Before these can be removed, one of bug 414812's tests must be updated
//       or it will likely fail!  Please CC jwalden+bmo on the bug associated
//       with removing these so he can provide a patch to make the necessary
//       changes to avoid bustage.
// ".test" localised TLDs for ICANN's top-level IDN trial
pref("network.IDN.whitelist.xn--0zwm56d", true);
pref("network.IDN.whitelist.xn--11b5bs3a9aj6g", true);
pref("network.IDN.whitelist.xn--80akhbyknj4f", true);
pref("network.IDN.whitelist.xn--9t4b11yi5a", true);
pref("network.IDN.whitelist.xn--deba0ad", true);
pref("network.IDN.whitelist.xn--g6w251d", true);
pref("network.IDN.whitelist.xn--hgbk6aj7f53bba", true);
pref("network.IDN.whitelist.xn--hlcj6aya9esc7a", true);
pref("network.IDN.whitelist.xn--jxalpdlp", true);
pref("network.IDN.whitelist.xn--kgbechtv", true);
pref("network.IDN.whitelist.xn--zckzah", true);

// If a domain includes any of the following characters, it may be a spoof 
// attempt and so we always display the domain name as punycode. This would 
// override the settings "network.IDN_show_punycode" and 
// "network.IDN.whitelist.*".
pref("network.IDN.blacklist_chars", "\u0020\u00A0\u00BC\u00BD\u00BE\u01C3\u02D0\u0337\u0338\u0589\u05C3\u05F4\u0609\u060A\u066A\u06D4\u0701\u0702\u0703\u0704\u115F\u1160\u1735\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u2024\u2027\u2028\u2029\u202F\u2039\u203A\u2041\u2044\u2052\u205F\u2153\u2154\u2155\u2156\u2157\u2158\u2159\u215A\u215B\u215C\u215D\u215E\u215F\u2215\u2236\u23AE\u2571\u29F6\u29F8\u2AFB\u2AFD\u2FF0\u2FF1\u2FF2\u2FF3\u2FF4\u2FF5\u2FF6\u2FF7\u2FF8\u2FF9\u2FFA\u2FFB\u3000\u3002\u3014\u3015\u3033\u3164\u321D\u321E\u33AE\u33AF\u33C6\u33DF\uA789\uFE14\uFE15\uFE3F\uFE5D\uFE5E\uFEFF\uFF0E\uFF0F\uFF61\uFFA0\uFFF9\uFFFA\uFFFB\uFFFC\uFFFD");

// This preference specifies a list of domains for which DNS lookups will be
// IPv4 only. Works around broken DNS servers which can't handle IPv6 lookups
// and/or allows the user to disable IPv6 on a per-domain basis. See bug 68796.
pref("network.dns.ipv4OnlyDomains", "");

// This preference can be used to turn off IPv6 name lookups. See bug 68796.
pref("network.dns.disableIPv6", false);

// The grace period allows the DNS cache to use expired entries, while kicking off
// a revalidation in the background. In seconds, but rounded to minutes in gecko.
// Default to 30 days. (basically forever)
pref("network.dnsCacheExpirationGracePeriod", 2592000);

// This preference can be used to turn off DNS prefetch.
pref("network.dns.disablePrefetch", false);

// This preference controls whether or not URLs with UTF-8 characters are
// escaped.  Set this preference to TRUE for strict RFC2396 conformance.
pref("network.standard-url.escape-utf8", true);

// This preference controls whether or not URLs are always encoded and sent as
// UTF-8.
pref("network.standard-url.encode-utf8", true);

// Idle timeout for ftp control connections - 5 minute default
pref("network.ftp.idleConnectionTimeout", 300);

// directory listing format
// 2: HTML
// 3: XUL directory viewer
// all other values are treated like 2
pref("network.dir.format", 2);

// enables the prefetch service (i.e., prefetching of <link rel="next"> URLs).
pref("network.prefetch-next", true);


// The following prefs pertain to the negotiate-auth extension (see bug 17578),
// which provides transparent Kerberos or NTLM authentication using the SPNEGO
// protocol.  Each pref is a comma-separated list of keys, where each key has
// the format:
//   [scheme "://"] [host [":" port]]
// For example, "foo.com" would match "http://www.foo.com/bar", etc.

// This list controls which URIs can use the negotiate-auth protocol.  This
// list should be limited to the servers you know you'll need to login to.
pref("network.negotiate-auth.trusted-uris", "");
// This list controls which URIs can support delegation.
pref("network.negotiate-auth.delegation-uris", "");

// Do not allow SPNEGO by default when challenged by a local server.
pref("network.negotiate-auth.allow-non-fqdn", false);

// Allow SPNEGO by default when challenged by a proxy server.
pref("network.negotiate-auth.allow-proxies", true);

// Path to a specific gssapi library
pref("network.negotiate-auth.gsslib", "");

// Specify if the gss lib comes standard with the OS
pref("network.negotiate-auth.using-native-gsslib", true);

//@line 1316 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Controls which NTLM authentication implementation we default to. True forces
// the use of our generic (internal) NTLM authentication implementation vs. any
// native implementation provided by the os. This pref is for diagnosing issues
// with native NTLM. (See bug 520607 for details.) Using generic NTLM authentication
// can expose the user to reflection attack vulnerabilities. Do not change this
// unless you know what you're doing!
// This pref should be removed 6 months after the release of firefox 3.6. 
pref("network.auth.force-generic-ntlm", false);

// The following prefs are used to enable automatic use of the operating
// system's NTLM implementation to silently authenticate the user with their
// Window's domain logon.  The trusted-uris pref follows the format of the
// trusted-uris pref for negotiate authentication.
pref("network.automatic-ntlm-auth.allow-proxies", true);
pref("network.automatic-ntlm-auth.allow-non-fqdn", false);
pref("network.automatic-ntlm-auth.trusted-uris", "");

// This preference controls whether or not the LM hash will be included in
// response to a NTLM challenge.  By default, this is disabled since servers
// should almost never need the LM hash, and the LM hash is what makes NTLM
// authentication less secure.  See bug 250691 for further details.
// NOTE: automatic-ntlm-auth which leverages the OS-provided NTLM
//       implementation will not be affected by this preference.
pref("network.ntlm.send-lm-response", false);

pref("permissions.default.image",           1); // 1-Accept, 2-Deny, 3-dontAcceptForeign

pref("network.proxy.type",                  5);
pref("network.proxy.ftp",                   "");
pref("network.proxy.ftp_port",              0);
pref("network.proxy.http",                  "");
pref("network.proxy.http_port",             0);
pref("network.proxy.ssl",                   "");
pref("network.proxy.ssl_port",              0);
pref("network.proxy.socks",                 "");
pref("network.proxy.socks_port",            0);
pref("network.proxy.socks_version",         5);
pref("network.proxy.socks_remote_dns",      false);
pref("network.proxy.no_proxies_on",         "localhost, 127.0.0.1");
pref("network.proxy.failover_timeout",      1800); // 30 minutes
pref("network.online",                      true); //online/offline
pref("network.cookie.cookieBehavior",       0); // 0-Accept, 1-dontAcceptForeign, 2-dontUse, 3-limitForeign
//@line 1365 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("network.cookie.thirdparty.sessionOnly", false);
pref("network.cookie.lifetimePolicy",       0); // accept normally, 1-askBeforeAccepting, 2-acceptForSession,3-acceptForNDays
pref("network.cookie.alwaysAcceptSessionCookies", false);
pref("network.cookie.prefsMigrated",        false);
pref("network.cookie.lifetime.days",        90);

// The PAC file to load.  Ignored unless network.proxy.type is 2.
pref("network.proxy.autoconfig_url", "");

// If we cannot load the PAC file, then try again (doubling from interval_min
// until we reach interval_max or the PAC file is successfully loaded).
pref("network.proxy.autoconfig_retry_interval_min", 5);    // 5 seconds
pref("network.proxy.autoconfig_retry_interval_max", 300);  // 5 minutes

// Use the HSTS preload list by default
pref("network.stricttransportsecurity.preloadlist", true);

pref("converter.html2txt.structs",          true); // Output structured phrases (strong, em, code, sub, sup, b, i, u)
pref("converter.html2txt.header_strategy",  1); // 0 = no indention; 1 = indention, increased with header level; 2 = numbering and slight indention

pref("intl.accept_languages",               "chrome://global/locale/intl.properties");
pref("intl.menuitems.alwaysappendaccesskeys","chrome://global/locale/intl.properties");
pref("intl.menuitems.insertseparatorbeforeaccesskeys","chrome://global/locale/intl.properties");
pref("intl.charsetmenu.browser.static",     "chrome://global/locale/intl.properties");
pref("intl.charsetmenu.browser.more1",      "ISO-8859-1, ISO-8859-15, IBM850, macintosh, windows-1252, ISO-8859-14, ISO-8859-7, x-mac-greek, windows-1253, x-mac-icelandic, ISO-8859-10, ISO-8859-3");
pref("intl.charsetmenu.browser.more2",      "ISO-8859-4, ISO-8859-13, windows-1257, IBM852, ISO-8859-2, x-mac-ce, windows-1250, x-mac-croatian, IBM855, ISO-8859-5, ISO-IR-111, KOI8-R, x-mac-cyrillic, windows-1251, IBM866, KOI8-U, x-mac-ukrainian, ISO-8859-16, x-mac-romanian");
pref("intl.charsetmenu.browser.more3",      "GB2312, gbk, gb18030, HZ-GB-2312, ISO-2022-CN, Big5, Big5-HKSCS, x-euc-tw, EUC-JP, ISO-2022-JP, Shift_JIS, EUC-KR, x-johab, ISO-2022-KR");
pref("intl.charsetmenu.browser.more4",      "armscii-8, TIS-620, ISO-8859-11, windows-874, IBM857, ISO-8859-9, x-mac-turkish, windows-1254, x-viet-tcvn5712, VISCII, x-viet-vps, windows-1258, x-mac-devanagari, x-mac-gujarati, x-mac-gurmukhi");
pref("intl.charsetmenu.browser.more5",      "ISO-8859-6, windows-1256, ISO-8859-8-I, windows-1255, ISO-8859-8, IBM862");
pref("intl.charsetmenu.mailedit",           "chrome://global/locale/intl.properties");
pref("intl.charsetmenu.browser.cache",      "");
pref("intl.charsetmenu.mailview.cache",     "");
pref("intl.charsetmenu.composer.cache",     "");
pref("intl.charsetmenu.browser.cache.size", 5);
pref("intl.charset.detector",               "chrome://global/locale/intl.properties");
pref("intl.charset.default",                "chrome://global-platform/locale/intl.properties");
pref("intl.ellipsis",                       "chrome://global-platform/locale/intl.properties");
pref("intl.locale.matchOS",                 false);
// fallback charset list for Unicode conversion (converting from Unicode)
// currently used for mail send only to handle symbol characters (e.g Euro, trademark, smartquotes)
// for ISO-8859-1
pref("intl.fallbackCharsetList.ISO-8859-1", "windows-1252");
pref("font.language.group",                 "chrome://global/locale/intl.properties");

// these locales have right-to-left UI
pref("intl.uidirection.ar", "rtl");
pref("intl.uidirection.he", "rtl");
pref("intl.uidirection.fa", "rtl");
pref("intl.uidirection.ur", "rtl");

// use en-US hyphenation by default for content tagged with plain lang="en"
pref("intl.hyphenation-alias.en", "en-us");
// and for other subtags of en-*, if no specific patterns are available
pref("intl.hyphenation-alias.en-*", "en-us");

pref("intl.hyphenation-alias.af-*", "af");
pref("intl.hyphenation-alias.bg-*", "bg");
pref("intl.hyphenation-alias.ca-*", "ca");
pref("intl.hyphenation-alias.cy-*", "cy");
pref("intl.hyphenation-alias.da-*", "da");
pref("intl.hyphenation-alias.eo-*", "eo");
pref("intl.hyphenation-alias.es-*", "es");
pref("intl.hyphenation-alias.et-*", "et");
pref("intl.hyphenation-alias.fi-*", "fi");
pref("intl.hyphenation-alias.fr-*", "fr");
pref("intl.hyphenation-alias.gl-*", "gl");
pref("intl.hyphenation-alias.hr-*", "hr");
pref("intl.hyphenation-alias.hsb-*", "hsb");
pref("intl.hyphenation-alias.hu-*", "hu");
pref("intl.hyphenation-alias.ia-*", "ia");
pref("intl.hyphenation-alias.is-*", "is");
pref("intl.hyphenation-alias.it-*", "it");
pref("intl.hyphenation-alias.kmr-*", "kmr");
pref("intl.hyphenation-alias.la-*", "la");
pref("intl.hyphenation-alias.lt-*", "lt");
pref("intl.hyphenation-alias.mn-*", "mn");
pref("intl.hyphenation-alias.nl-*", "nl");
pref("intl.hyphenation-alias.pt-*", "pt");
pref("intl.hyphenation-alias.ru-*", "ru");
pref("intl.hyphenation-alias.sl-*", "sl");
pref("intl.hyphenation-alias.sv-*", "sv");
pref("intl.hyphenation-alias.tr-*", "tr");
pref("intl.hyphenation-alias.uk-*", "uk");

// use reformed (1996) German patterns by default unless specifically tagged as de-1901
// (these prefs may soon be obsoleted by better BCP47-based tag matching, but for now...)
pref("intl.hyphenation-alias.de", "de-1996");
pref("intl.hyphenation-alias.de-*", "de-1996");
pref("intl.hyphenation-alias.de-AT-1901", "de-1901");
pref("intl.hyphenation-alias.de-DE-1901", "de-1901");
pref("intl.hyphenation-alias.de-CH-*", "de-CH");

// patterns from TeX are tagged as "sh" (Serbo-Croatian) macrolanguage;
// alias "sr" (Serbian) and "bs" (Bosnian) to those patterns
// (Croatian has its own separate patterns).
pref("intl.hyphenation-alias.sr", "sh");
pref("intl.hyphenation-alias.bs", "sh");
pref("intl.hyphenation-alias.sh-*", "sh");
pref("intl.hyphenation-alias.sr-*", "sh");
pref("intl.hyphenation-alias.bs-*", "sh");

// Norwegian has two forms, Bokmål and Nynorsk, with "no" as a macrolanguage encompassing both.
// For "no", we'll alias to "nb" (Bokmål) as that is the more widely used written form.
pref("intl.hyphenation-alias.no", "nb");
pref("intl.hyphenation-alias.no-*", "nb");
pref("intl.hyphenation-alias.nb-*", "nb");
pref("intl.hyphenation-alias.nn-*", "nn");

pref("font.mathfont-family", "MathJax_Main, STIXNonUnicode, STIXSizeOneSym, STIXSize1, STIXGeneral, Asana Math, Standard Symbols L, DejaVu Sans, Cambria Math");

// Some CJK fonts have bad underline offset, their CJK character glyphs are overlapped (or adjoined)  to its underline.
// These fonts are ignored the underline offset, instead of it, the underline is lowered to bottom of its em descent.
pref("font.blacklist.underline_offset", "FangSong,Gulim,GulimChe,MingLiU,MingLiU-ExtB,MingLiU_HKSCS,MingLiU-HKSCS-ExtB,MS Gothic,MS Mincho,MS PGothic,MS PMincho,MS UI Gothic,PMingLiU,PMingLiU-ExtB,SimHei,SimSun,SimSun-ExtB,Hei,Kai,Apple LiGothic,Apple LiSung,Osaka");

pref("images.dither", "auto");
pref("security.directory",              "");

pref("signed.applets.codebase_principal_support", false);
pref("security.checkloaduri", true);
pref("security.xpconnect.plugin.unrestricted", true);
// security-sensitive dialogs should delay button enabling. In milliseconds.
pref("security.dialog_enable_delay", 2000);
pref("security.notification_enable_delay", 500);

pref("security.csp.enable", true);
pref("security.csp.debug", false);

// Mixed content blocking
pref("security.mixed_content.block_active_content", false);
pref("security.mixed_content.block_display_content", false);

// Modifier key prefs: default to Windows settings,
// menu access key = alt, accelerator key = control.
// Use 17 for Ctrl, 18 for Alt, 224 for Meta, 91 for Win, 0 for none. Mac settings in macprefs.js
pref("ui.key.accelKey", 17);
pref("ui.key.menuAccessKey", 18);
pref("ui.key.generalAccessKey", -1);

// If generalAccessKey is -1, use the following two prefs instead.
// Use 0 for disabled, 1 for Shift, 2 for Ctrl, 4 for Alt, 8 for Meta, 16 for Win
// (values can be combined, e.g. 5 for Alt+Shift)
pref("ui.key.chromeAccess", 4);
pref("ui.key.contentAccess", 5);

pref("ui.key.menuAccessKeyFocuses", false); // overridden below
pref("ui.key.saveLink.shift", true); // true = shift, false = meta

// Disable page loading activity cursor by default.
pref("ui.use_activity_cursor", false);

// Middle-mouse handling
pref("middlemouse.paste", false);
pref("middlemouse.openNewWindow", true);
pref("middlemouse.contentLoadURL", false);
pref("middlemouse.scrollbarPosition", false);

// Clipboard behavior
pref("clipboard.autocopy", false);

// mouse wheel scroll transaction period of time (in milliseconds)
pref("mousewheel.transaction.timeout", 1500);
// mouse wheel scroll transaction is held even if the mouse cursor is moved.
pref("mousewheel.transaction.ignoremovedelay", 100);

// prefs for app level mouse wheel scrolling acceleration.
// number of mousewheel clicks when acceleration starts
// acceleration can be turned off if pref is set to -1
pref("mousewheel.acceleration.start", -1);
// factor to be multiplied for constant acceleration
pref("mousewheel.acceleration.factor", 10);

// Prefs for override the system mouse wheel scrolling speed on the root
// content of the web pages.  When
// "mousewheel.system_scroll_override_on_root_content.enabled" is true and the system
// scrolling speed isn't customized by the user, the root content scrolling
// speed is multiplied by the following factors.  The value will be used as
// 1/100.  E.g., 200 means 2.00.
// NOTE: Even if "mousewheel.system_scroll_override_on_root_content.enabled" is
// true, when Gecko detects the user customized the system scrolling speed
// settings, the override isn't executed.
pref("mousewheel.system_scroll_override_on_root_content.vertical.factor", 200);
pref("mousewheel.system_scroll_override_on_root_content.horizontal.factor", 200);

// mousewheel.*.action can specify the action when you use mosue wheel.
// When no modifier keys are pressed or two or more modifires are pressed,
// .default is used.
// 0: Nothing happens
// 1: Scrolling contents
// 2: Go back or go forward, in your history
// 3: Zoom in or out.
pref("mousewheel.default.action", 1);
pref("mousewheel.with_alt.action", 2);
pref("mousewheel.with_control.action", 3);
pref("mousewheel.with_meta.action", 1);  // command key on Mac
pref("mousewheel.with_shift.action", 1);
pref("mousewheel.with_win.action", 1);

// mousewheel.*.action.override_x will override the action
// when the mouse wheel is rotated along the x direction.
// -1: Don't override the action.
// 0 to 3: Override the action with the specified value.
pref("mousewheel.default.action.override_x", -1);
pref("mousewheel.with_alt.action.override_x", -1);
pref("mousewheel.with_control.action.override_x", -1);
pref("mousewheel.with_meta.action.override_x", -1);  // command key on Mac
pref("mousewheel.with_shift.action.override_x", -1);
pref("mousewheel.with_win.action.override_x", -1);

// mousewheel.*.delta_multiplier_* can specify the value muliplied by the delta
// value.  The values will be used after divided by 100.  I.e., 100 means 1.0,
// -100 means -1.0.  If the values were negative, the direction would be
// reverted.  The absolue value must be 100 or larger.
pref("mousewheel.default.delta_multiplier_x", 100);
pref("mousewheel.default.delta_multiplier_y", 100);
pref("mousewheel.default.delta_multiplier_z", 100);
pref("mousewheel.with_alt.delta_multiplier_x", 100);
pref("mousewheel.with_alt.delta_multiplier_y", 100);
pref("mousewheel.with_alt.delta_multiplier_z", 100);
pref("mousewheel.with_control.delta_multiplier_x", 100);
pref("mousewheel.with_control.delta_multiplier_y", 100);
pref("mousewheel.with_control.delta_multiplier_z", 100);
pref("mousewheel.with_meta.delta_multiplier_x", 100);  // command key on Mac
pref("mousewheel.with_meta.delta_multiplier_y", 100);  // command key on Mac
pref("mousewheel.with_meta.delta_multiplier_z", 100);  // command key on Mac
pref("mousewheel.with_shift.delta_multiplier_x", 100);
pref("mousewheel.with_shift.delta_multiplier_y", 100);
pref("mousewheel.with_shift.delta_multiplier_z", 100);
pref("mousewheel.with_win.delta_multiplier_x", 100);
pref("mousewheel.with_win.delta_multiplier_y", 100);
pref("mousewheel.with_win.delta_multiplier_z", 100);

// If line-height is lower than this value (in device pixels), 1 line scroll
// scrolls this height.
pref("mousewheel.min_line_scroll_amount", 5);

// These define the smooth scroll behavior (min ms, max ms) for different triggers
// Some triggers:
// mouseWheel: Discrete mouse wheel events, Synaptics touchpads on windows (generate wheel events)
// Lines:  Up/Down/Left/Right KB arrows
// Pages:  Page up/down, Space
// Scrollbars: Clicking scrollbars arrows, clicking scrollbars tracks
// Note: Currently OS X trackpad and magic mouse don't use our smooth scrolling
// Note: These are relevant only when "general.smoothScroll" is enabled
pref("general.smoothScroll.mouseWheel.durationMinMS", 200);
pref("general.smoothScroll.mouseWheel.durationMaxMS", 400);
pref("general.smoothScroll.pixels.durationMinMS", 150);
pref("general.smoothScroll.pixels.durationMaxMS", 150);
pref("general.smoothScroll.lines.durationMinMS", 150);
pref("general.smoothScroll.lines.durationMaxMS", 150);
pref("general.smoothScroll.pages.durationMinMS", 150);
pref("general.smoothScroll.pages.durationMaxMS", 150);
pref("general.smoothScroll.scrollbars.durationMinMS", 150);
pref("general.smoothScroll.scrollbars.durationMaxMS", 150);
pref("general.smoothScroll.other.durationMinMS", 150);
pref("general.smoothScroll.other.durationMaxMS", 150);
// Enable disable smooth scrolling for different triggers (when "general.smoothScroll" is enabled)
pref("general.smoothScroll.mouseWheel", true);
pref("general.smoothScroll.pixels", true);
pref("general.smoothScroll.lines", true);
pref("general.smoothScroll.pages", true);
pref("general.smoothScroll.scrollbars", true);
pref("general.smoothScroll.other", true);
// To connect consecutive scroll events into a continuous flow, the animation's duration
// should be longer than scroll events intervals (or else the scroll will stop
// before the next event arrives - we're guessing next interval by averaging recent
// intervals).
// This defines how longer is the duration compared to events interval (percentage)
pref("general.smoothScroll.durationToIntervalRatio", 200);

pref("profile.confirm_automigration",true);
// profile.migration_behavior determines how the profiles root is set
// 0 - use NS_APP_USER_PROFILES_ROOT_DIR
// 1 - create one based on the NS4.x profile root
// 2 - use, if not empty, profile.migration_directory otherwise same as 0
pref("profile.migration_behavior",0);
pref("profile.migration_directory", "");

// the amount of time (in seconds) that must elapse
// before we think your mozilla profile is defunct
// and you'd benefit from re-migrating from 4.x
// see bug #137886 for more details
//
// if -1, we never think your profile is defunct
// and users will never see the remigrate UI.
pref("profile.seconds_until_defunct", -1);
// We can show it anytime from menus
pref("profile.manage_only_at_launch", false);

pref("prefs.converted-to-utf8",false);

// --------------------------------------------------
// IBMBIDI 
// --------------------------------------------------
//
// ------------------
//  Text Direction
// ------------------
// 1 = directionLTRBidi *
// 2 = directionRTLBidi
pref("bidi.direction", 1);
// ------------------
//  Text Type
// ------------------
// 1 = charsettexttypeBidi *
// 2 = logicaltexttypeBidi
// 3 = visualtexttypeBidi
pref("bidi.texttype", 1);
// ------------------
//  Numeral Style
// ------------------
// 0 = nominalnumeralBidi *
// 1 = regularcontextnumeralBidi
// 2 = hindicontextnumeralBidi
// 3 = arabicnumeralBidi
// 4 = hindinumeralBidi
// 5 = persiancontextnumeralBidi
// 6 = persiannumeralBidi
pref("bidi.numeral", 0);
// ------------------
//  Support Mode
// ------------------
// 1 = mozillaBidisupport *
// 2 = OsBidisupport
// 3 = disableBidisupport
pref("bidi.support", 1);
// Whether delete and backspace should immediately delete characters not
// visually adjacent to the caret, or adjust the visual position of the caret
// on the first keypress and delete the character on a second keypress
pref("bidi.edit.delete_immediately", false);

// Bidi caret movement style:
// 0 = logical
// 1 = visual
// 2 = visual, but logical during selection
pref("bidi.edit.caret_movement_style", 2);

// Setting this pref to |true| forces Bidi UI menu items and keyboard shortcuts
// to be exposed, and enables the directional caret hook. By default, only
// expose it for bidi-associated system locales.
pref("bidi.browser.ui", false);

// used for double-click word selection behavior. Win will override.
pref("layout.word_select.eat_space_to_next_word", false);
pref("layout.word_select.stop_at_punctuation", true);

// controls caret style and word-delete during text selection
// 0 = use platform default
// 1 = caret moves and blinks as when there is no selection; word
//     delete deselects the selection and then deletes word
// 2 = caret moves to selection edge and is not visible during selection; 
//     word delete deletes the selection (Mac and Linux default)
// 3 = caret moves and blinks as when there is no selection; word delete
//     deletes the selection
// Windows default is 1 for word delete behavior, the rest as for 2.
pref("layout.selection.caret_style", 0);

// pref to control whether or not to replace backslashes with Yen signs
// in documents encoded in one of Japanese legacy encodings (EUC-JP, 
// Shift_JIS, ISO-2022-JP)
pref("layout.enable_japanese_specific_transform", false);

// pref to force frames to be resizable
pref("layout.frames.force_resizability", false);

// pref to report CSS errors to the error console
pref("layout.css.report_errors", true);

// Should the :visited selector ever match (otherwise :link matches instead)?
pref("layout.css.visited_links_enabled", true);

// Override DPI. A value of -1 means use the maximum of 96 and the system DPI.
// A value of 0 means use the system DPI. A positive value is used as the DPI.
// This sets the physical size of a device pixel and thus controls the
// interpretation of physical units such as "pt".
pref("layout.css.dpi", -1);

// Set the number of device pixels per CSS pixel. A value <= 0 means choose
// automatically based on user settings for the platform (e.g., "UI scale factor"
// on Mac). A positive value is used as-is. This effectively controls the size
// of a CSS "px". This is only used for windows on the screen, not for printing.
pref("layout.css.devPixelsPerPx", "-1.0");

// Is support for CSS Masking features enabled?
//@line 1749 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("layout.css.masking.enabled", false);
//@line 1753 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Is support for the the @supports rule enabled?
pref("layout.css.supports-rule.enabled", true);

// Is support for CSS Flexbox enabled?
pref("layout.css.flexbox.enabled", true);

// Is support for CSS3 Fonts features enabled?
// (includes font-variant-*, font-kerning, font-synthesis
// and the @font-feature-values rule)
// Note: with this enabled, font-feature-settings is aliased
// to -moz-font-feature-settings.  When unprefixing, this should
// be reversed, -moz-font-feature-settings should alias to
// font-feature-settings.
//@line 1768 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("layout.css.font-features.enabled", false);
//@line 1772 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Are sets of prefixed properties supported?
pref("layout.css.prefixes.border-image", true);
pref("layout.css.prefixes.transforms", true);
pref("layout.css.prefixes.transitions", true);
pref("layout.css.prefixes.animations", true);

// Is support for the :scope selector enabled?
//@line 1781 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("layout.css.scope-pseudo.enabled", false);
//@line 1785 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Is support for CSS vertical text enabled?
pref("layout.css.vertical-text.enabled", false);

// pref for which side vertical scrollbars should be on
// 0 = end-side in UI direction
// 1 = end-side in document/content direction
// 2 = right
// 3 = left
pref("layout.scrollbar.side", 0);

// pref to control browser frame rate, in Hz. A value <= 0 means choose
// automatically based on knowledge of the platform (or 60Hz if no platform-
// specific information is available).
pref("layout.frame_rate", -1);

// pref to control precision of the frame rate timer. When true,
// we use a "precise" timer, which means each notification fires
// Nms after the start of the last notification. That means if the
// processing of the notification is slow, the timer can fire immediately
// after we've just finished processing the last notification, which might
// lead to starvation problems.
// When false, we use a "slack" timer which fires Nms after the *end*
// of the last notification. This can give less tight frame rates
// but provides more time for other operations when the browser is
// heavily loaded.
pref("layout.frame_rate.precise", false);

// pref to permit users to make verified SOAP calls by default
pref("capability.policy.default.SOAPCall.invokeVerifySourceHeader", "allAccess");

// if true, allow plug-ins to override internal imglib decoder mime types in full-page mode
pref("plugin.override_internal_types", false);

// See bug 136985.  Gives embedders a pref to hook into to show
// a popup blocker if they choose.
pref("browser.popups.showPopupBlocker", true);

// Pref to control whether the viewmanager code does double-buffering or not
// See http://bugzilla.mozilla.org/show_bug.cgi?id=169483 for further details...
pref("viewmanager.do_doublebuffering", true);

// enable single finger gesture input (win7+ tablets)
pref("gestures.enable_single_finger_input", true);

pref("editor.resizing.preserve_ratio",       true);
pref("editor.positioning.offset",            0);

pref("dom.max_chrome_script_run_time", 20);
pref("dom.max_script_run_time", 10);

// If true, ArchiveReader will be enabled
pref("dom.archivereader.enabled", false);

// If true, Future will be enabled
//@line 1841 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("dom.future.enabled", false);
//@line 1845 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Hang monitor timeout after which we kill the browser, in seconds
// (0 is disabled)
// Disabled on all platforms per bug 705748 until the found issues are
// resolved.
pref("hangmonitor.timeout", 0);

pref("plugins.load_appdir_plugins", false);
// If true, plugins will be click to play
pref("plugins.click_to_play", false);
// The default value for nsIPluginTag.enabledState (STATE_ENABLED = 2)
pref("plugin.default.state", 2);

// How long in minutes we will allow a plugin to work after the user has chosen
// to allow it "now"
pref("plugin.sessionPermissionNow.intervalInMinutes", 60);
// How long in days we will allow a plugin to work after the user has chosen
// to allow it persistently.
pref("plugin.persistentPermissionAlways.intervalInDays", 90);

//@line 1866 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
// How long a plugin is allowed to process a synchronous IPC message
// before we consider it "hung".
pref("dom.ipc.plugins.timeoutSecs", 45);
// How long a plugin process will wait for a response from the parent
// to a synchronous request before terminating itself. After this
// point the child assumes the parent is hung. Currently disabled.
pref("dom.ipc.plugins.parentTimeoutSecs", 0);
// How long a plugin launch is allowed to take before
// we consider it failed.
pref("dom.ipc.plugins.processLaunchTimeoutSecs", 45);
//@line 1883 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
// How long a content process can take before closing its IPC channel
// after shutdown is initiated.  If the process exceeds the timeout,
// we fear the worst and kill it.
pref("dom.ipc.tabs.shutdownTimeoutSecs", 5);
//@line 1898 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 1904 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

pref("dom.ipc.plugins.flash.subprocess.crashreporter.enabled", true);
pref("dom.ipc.plugins.reportCrashURL", true);

pref("dom.ipc.processCount", 1);

// Enable the use of display-lists for SVG hit-testing and painting.
pref("svg.display-lists.hit-testing.enabled", true);
pref("svg.display-lists.painting.enabled", true);

// Is support for the SVG 2 paint-order property enabled?
//@line 1916 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("svg.paint-order.enabled", false);
//@line 1920 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Is support for the new SVG text implementation enabled?
pref("svg.text.css-frames.enabled", false);

pref("font.minimum-size.ar", 0);
pref("font.minimum-size.x-armn", 0);
pref("font.minimum-size.x-beng", 0);
pref("font.minimum-size.x-baltic", 0);
pref("font.minimum-size.x-central-euro", 0);
pref("font.minimum-size.zh-CN", 0);
pref("font.minimum-size.zh-HK", 0);
pref("font.minimum-size.zh-TW", 0);
pref("font.minimum-size.x-cyrillic", 0);
pref("font.minimum-size.x-devanagari", 0);
pref("font.minimum-size.x-ethi", 0);
pref("font.minimum-size.x-geor", 0);
pref("font.minimum-size.el", 0);
pref("font.minimum-size.x-gujr", 0);
pref("font.minimum-size.x-guru", 0);
pref("font.minimum-size.he", 0);
pref("font.minimum-size.ja", 0);
pref("font.minimum-size.x-knda", 0);
pref("font.minimum-size.x-khmr", 0);
pref("font.minimum-size.ko", 0);
pref("font.minimum-size.x-mlym", 0);
pref("font.minimum-size.x-orya", 0);
pref("font.minimum-size.x-sinh", 0);
pref("font.minimum-size.x-tamil", 0);
pref("font.minimum-size.x-telu", 0);
pref("font.minimum-size.x-tibt", 0);
pref("font.minimum-size.th", 0);
pref("font.minimum-size.tr", 0);
pref("font.minimum-size.x-cans", 0);
pref("font.minimum-size.x-western", 0);
pref("font.minimum-size.x-unicode", 0);
pref("font.minimum-size.x-user-def", 0);

/*
 * A value greater than zero enables font size inflation for
 * pan-and-zoom UIs, so that the fonts in a block are at least the size
 * that, if a block's width is scaled to match the device's width, the
 * fonts in the block are big enough that at most the pref value ems of
 * text fit in *the width of the device*.
 *
 * When both this pref and the next are set, the larger inflation is
 * used.
 */
pref("font.size.inflation.emPerLine", 0);
/*
 * A value greater than zero enables font size inflation for
 * pan-and-zoom UIs, so that if a block's width is scaled to match the
 * device's width, the fonts in a block are at least the font size
 * given.  The value given is in twips, i.e., 1/20 of a point, or 1/1440
 * of an inch.
 *
 * When both this pref and the previous are set, the larger inflation is
 * used.
 */
pref("font.size.inflation.minTwips", 0);
/*
 * In products with multi-mode pan-and-zoom and non-pan-and-zoom UIs,
 * this pref forces font inflation to always be enabled in all modes.
 * That is, any heuristics used to detect pan-and-zoom
 * vs. non-pan-and-zoom modes are disabled and all content is treated
 * as pan-and-zoom mode wrt font inflation.
 *
 * This pref has no effect if font inflation is not enabled through
 * either of the prefs above.  It has no meaning in single-mode UIs.
 */
pref("font.size.inflation.forceEnabled", false);
/*
 * In products with multi-mode pan-and-zoom and non-pan-and-zoom UIs,
 * this pref disables font inflation in master-process contexts where
 * existing heuristics can't be used determine enabled-ness.
 *
 * This pref has no effect if font inflation is not enabled through
 * either of the prefs above.  The "forceEnabled" pref above overrides
 * this pref.
 */
pref("font.size.inflation.disabledInMasterProcess", false);
/*
 * Since the goal of font size inflation is to avoid having to
 * repeatedly scroll side to side to read a block of text, and there are
 * a number of page layouts where a relatively small chunk of text is
 * better of not being inflated according to the same algorithm we use
 * for larger chunks of text, we want a threshold for an amount of text
 * that triggers font size inflation.  This preference controls that
 * threshold.
 *
 * It controls the threshold used within an *approximation* of the
 * number of lines of text we use.  In particular, if we assume that
 * each character (collapsing collapsible whitespace) has a width the
 * same as the em-size of the font (when, normally, it's actually quite
 * a bit smaller on average), this preference gives the percentage of a
 * number of lines of text we'd need to trigger inflation.  This means
 * that a percentage of 100 means that we'd need a number of characters
 * (we know the font size and the width) equivalent to one line of
 * square text (which is actually a lot less than a real line of text).
 *
 * A value of 0 means there's no character length threshold.
 */
pref("font.size.inflation.lineThreshold", 400);

/*
 * Defines the font size inflation mapping intercept parameter.
 *
 * Font size inflation computes a minimum font size, m, based on
 * other preferences (see font.size.inflation.minTwips and
 * font.size.inflation.emPerLine, above) and the width of the
 * frame in which the text resides. Using this minimum, a specified
 * font size, s, is mapped to an inflated font size, i, using an
 * equation that varies depending on the value of the font size
 * inflation mapping intercept parameter, P:
 *
 * If the intercept parameter is negative, then the following mapping
 * function is used:
 *
 * i = m + s
 *
 * If the intercept parameter is non-negative, then the mapping function
 * is a function such that its graph meets the graph of i = s at the
 * point where both i and s are (1 + P/2) * m for values of s that are
 * large enough. This means that when s=0, i is always equal to m.
 */
pref("font.size.inflation.mappingIntercept", 1);


/*
 * This controls the percentage that fonts will be inflated, if font
 * size inflation is enabled. Essentially, if we have a specified font
 * size, s, and an inflated font size, i, this specifies that the ratio
 * i/s * 100 should never exceed the value of this preference.
 *
 * In order for this preference to have any effect, its value must be
 * greater than 100, since font inflation can never decrease the ratio
 * i/s.
 */
pref("font.size.inflation.maxRatio", 0);

/*
 * When enabled, the touch.radius and mouse.radius prefs allow events to be dispatched
 * to nearby elements that are sensitive to the event. See PositionedEventTargeting.cpp.
 * The 'mm' prefs define a rectangle around the nominal event target point within which
 * we will search for suitable elements. 'visitedWeight' is a percentage weight;
 * a value > 100 makes a visited link be treated as further away from the event target
 * than it really is, while a value < 100 makes a visited link be treated as closer
 * to the event target than it really is.
 */
pref("ui.touch.radius.enabled", false);
pref("ui.touch.radius.leftmm", 8);
pref("ui.touch.radius.topmm", 12);
pref("ui.touch.radius.rightmm", 8);
pref("ui.touch.radius.bottommm", 4);
pref("ui.touch.radius.visitedWeight", 120);

pref("ui.mouse.radius.enabled", false);
pref("ui.mouse.radius.leftmm", 8);
pref("ui.mouse.radius.topmm", 12);
pref("ui.mouse.radius.rightmm", 8);
pref("ui.mouse.radius.bottommm", 4);
pref("ui.mouse.radius.visitedWeight", 120);

// When true, the ui.mouse.radius.* prefs will only affect simulated mouse events generated by touch input.
// When false, the prefs will be used for all mouse events.
pref("ui.mouse.radius.inputSource.touchOnly", true);

//@line 2544 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 2985 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 3181 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 3546 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 3550 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
// Handled differently under Mac/Windows
pref("network.protocol-handler.warn-external.file", false);
pref("browser.drag_out_of_frame_style", 1);

// Middle-mouse handling
pref("middlemouse.paste", true);
pref("middlemouse.contentLoadURL", true);
pref("middlemouse.openNewWindow", true);
pref("middlemouse.scrollbarPosition", true);

// Clipboard behavior
pref("clipboard.autocopy", true);

pref("browser.urlbar.clickSelectsAll", false);

// Tab focus model bit field:
// 1 focuses text controls, 2 focuses other form elements, 4 adds links.
// Leave this at the default, 7, to match mozilla1.0-era user expectations.
// pref("accessibility.tabfocus", 1);

// autocomplete keyboard grab workaround
pref("autocomplete.grab_during_popup", true);
pref("autocomplete.ungrab_during_mode_switch", true);

// Default to using the system filepicker if possible, but allow
// toggling to use the XUL filepicker
pref("ui.allow_platform_file_picker", true);

pref("helpers.global_mime_types_file", "/etc/mime.types");
pref("helpers.global_mailcap_file", "/etc/mailcap");
pref("helpers.private_mime_types_file", "~/.mime.types");
pref("helpers.private_mailcap_file", "~/.mailcap");
pref("print.print_command", "lpr ${MOZ_PRINTER_NAME:+-P\"$MOZ_PRINTER_NAME\"}");
pref("print.printer_list", ""); // list of printers, separated by spaces
pref("print.print_reversed", false);
pref("print.print_color", true);
pref("print.print_landscape", false);
pref("print.print_paper_size", 0);

// print_extra_margin enables platforms to specify an extra gap or margin
// around the content of the page for Print Preview only
pref("print.print_extra_margin", 0); // twips

// font names

pref("font.alias-list", "sans,sans-serif,serif,monospace");

// ar

pref("font.name.serif.el", "serif");
pref("font.name.sans-serif.el", "sans-serif");
pref("font.name.monospace.el", "monospace");

pref("font.name.serif.he", "serif");
pref("font.name.sans-serif.he", "sans-serif");
pref("font.name.monospace.he", "monospace");

pref("font.name.serif.ja", "serif");
pref("font.name.sans-serif.ja", "sans-serif");
pref("font.name.monospace.ja", "monospace");

pref("font.name.serif.ko", "serif");
pref("font.name.sans-serif.ko", "sans-serif");
pref("font.name.monospace.ko", "monospace");

pref("font.name.serif.th", "serif");
pref("font.name.sans-serif.th", "sans-serif");
pref("font.name.monospace.th", "monospace");

pref("font.name.serif.tr", "serif");
pref("font.name.sans-serif.tr", "sans-serif");
pref("font.name.monospace.tr", "monospace");

pref("font.name.serif.x-baltic", "serif");
pref("font.name.sans-serif.x-baltic", "sans-serif");
pref("font.name.monospace.x-baltic", "monospace");

pref("font.name.serif.x-central-euro", "serif");
pref("font.name.sans-serif.x-central-euro", "sans-serif");
pref("font.name.monospace.x-central-euro", "monospace");

pref("font.name.serif.x-cyrillic", "serif");
pref("font.name.sans-serif.x-cyrillic", "sans-serif");
pref("font.name.monospace.x-cyrillic", "monospace");

pref("font.name.serif.x-unicode", "serif");
pref("font.name.sans-serif.x-unicode", "sans-serif");
pref("font.name.monospace.x-unicode", "monospace");

pref("font.name.serif.x-user-def", "serif");
pref("font.name.sans-serif.x-user-def", "sans-serif");
pref("font.name.monospace.x-user-def", "monospace");

pref("font.name.serif.x-western", "serif");
pref("font.name.sans-serif.x-western", "sans-serif");
pref("font.name.monospace.x-western", "monospace");

pref("font.name.serif.zh-CN", "serif");
pref("font.name.sans-serif.zh-CN", "sans-serif");
pref("font.name.monospace.zh-CN", "monospace");

// ming_uni.ttf (HKSCS-2001) 
// http://www.info.gov.hk/digital21/eng/hkscs/download/uime.exe
pref("font.name.serif.zh-HK", "serif");
pref("font.name.sans-serif.zh-HK", "sans-serif");
pref("font.name.monospace.zh-HK", "monospace");

// zh-TW

pref("font.default.ar", "sans-serif");
pref("font.size.variable.ar", 16);
pref("font.size.fixed.ar", 12);

pref("font.default.el", "serif");
pref("font.size.variable.el", 16);
pref("font.size.fixed.el", 12);

pref("font.default.he", "sans-serif");
pref("font.size.variable.he", 16);
pref("font.size.fixed.he", 12);

pref("font.default.ja", "sans-serif");
pref("font.size.variable.ja", 16);
pref("font.size.fixed.ja", 16);

pref("font.default.ko", "sans-serif");
pref("font.size.variable.ko", 16);
pref("font.size.fixed.ko", 16);

pref("font.default.th", "serif");
pref("font.size.variable.th", 16);
pref("font.size.fixed.th", 13);
pref("font.minimum-size.th", 13);

pref("font.default.tr", "serif");
pref("font.size.variable.tr", 16);
pref("font.size.fixed.tr", 12);

pref("font.default.x-baltic", "serif");
pref("font.size.variable.x-baltic", 16);
pref("font.size.fixed.x-baltic", 12);

pref("font.default.x-central-euro", "serif");
pref("font.size.variable.x-central-euro", 16);
pref("font.size.fixed.x-central-euro", 12);

pref("font.default.x-cyrillic", "serif");
pref("font.size.variable.x-cyrillic", 16);
pref("font.size.fixed.x-cyrillic", 12);

pref("font.default.x-unicode", "serif");
pref("font.size.variable.x-unicode", 16);
pref("font.size.fixed.x-unicode", 12);

pref("font.default.x-user-def", "serif");
pref("font.size.variable.x-user-def", 16);
pref("font.size.fixed.x-user-def", 12);

pref("font.default.x-western", "serif");
pref("font.size.variable.x-western", 16);
pref("font.size.fixed.x-western", 12);

pref("font.default.zh-CN", "sans-serif");
pref("font.size.variable.zh-CN", 16);
pref("font.size.fixed.zh-CN", 16);

pref("font.default.zh-TW", "sans-serif");
pref("font.size.variable.zh-TW", 16);
pref("font.size.fixed.zh-TW", 16);

pref("font.default.zh-HK", "sans-serif");
pref("font.size.variable.zh-HK", 16);
pref("font.size.fixed.zh-HK", 16);

pref("font.default.x-devanagari", "serif");
pref("font.size.variable.x-devanagari", 16);
pref("font.size.fixed.x-devanagari", 13);

pref("font.default.x-tamil", "serif");
pref("font.size.variable.x-tamil", 16);
pref("font.size.fixed.x-tamil", 13);

pref("font.default.x-armn", "serif");
pref("font.size.variable.x-armn", 16);
pref("font.size.fixed.x-armn", 13);

pref("font.default.x-beng", "serif");
pref("font.size.variable.x-beng", 16);
pref("font.size.fixed.x-beng", 13);

pref("font.default.x-cans", "serif");
pref("font.size.variable.x-cans", 16);
pref("font.size.fixed.x-cans", 13);

pref("font.default.x-ethi", "serif");
pref("font.size.variable.x-ethi", 16);
pref("font.size.fixed.x-ethi", 13);

pref("font.default.x-geor", "serif");
pref("font.size.variable.x-geor", 16);
pref("font.size.fixed.x-geor", 13);

pref("font.default.x-gujr", "serif");
pref("font.size.variable.x-gujr", 16);
pref("font.size.fixed.x-gujr", 13);

pref("font.default.x-guru", "serif");
pref("font.size.variable.x-guru", 16);
pref("font.size.fixed.x-guru", 13);

pref("font.default.x-khmr", "serif");
pref("font.size.variable.x-khmr", 16);
pref("font.size.fixed.x-khmr", 13);

pref("font.default.x-mlym", "serif");
pref("font.size.variable.x-mlym", 16);
pref("font.size.fixed.x-mlym", 13);

pref("font.default.x-orya", "serif");
pref("font.size.variable.x-orya", 16);
pref("font.size.fixed.x-orya", 13);

pref("font.default.x-telu", "serif");
pref("font.size.variable.x-telu", 16);
pref("font.size.fixed.x-telu", 13);

pref("font.default.x-knda", "serif");
pref("font.size.variable.x-knda", 16);
pref("font.size.fixed.x-knda", 13);

pref("font.default.x-sinh", "serif");
pref("font.size.variable.x-sinh", 16);
pref("font.size.fixed.x-sinh", 13);

pref("font.default.x-tibt", "serif");
pref("font.size.variable.x-tibt", 16);
pref("font.size.fixed.x-tibt", 13);

/* PostScript print module prefs */
// pref("print.postscript.enabled",      true);
pref("print.postscript.paper_size",    "letter");
pref("print.postscript.orientation",   "portrait");
pref("print.postscript.print_command", "lpr ${MOZ_PRINTER_NAME:+-P\"$MOZ_PRINTER_NAME\"}");

// On GTK2 platform, we should use topmost window level for the default window
// level of <panel> element of XUL. GTK2 has only two window types. One is
// normal top level window, other is popup window. The popup window is always
// topmost window level, therefore, we are using normal top level window for
// non-topmost panel, but it is pretty hacky. On some Window Managers, we have
// 2 problems:
// 1. The non-topmost panel steals focus from its parent window at showing.
// 2. The parent of non-topmost panel is not activated when the panel is hidden.
// So, we have no reasons we should use non-toplevel window for popup.
pref("ui.panel.default_level_parent", true);

pref("mousewheel.system_scroll_override_on_root_content.enabled", false);

//@line 3811 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 3831 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 3839 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Login Manager prefs
pref("signon.rememberSignons",              true);
pref("signon.SignonFileName",               "signons.txt"); // obsolete 
pref("signon.SignonFileName2",              "signons2.txt"); // obsolete
pref("signon.SignonFileName3",              "signons3.txt"); // obsolete
pref("signon.autofillForms",                true);
pref("signon.autologin.proxy",              false);
pref("signon.debug",                        false);

// Satchel (Form Manager) prefs
pref("browser.formfill.debug",            false);
pref("browser.formfill.enable",           true);
pref("browser.formfill.expire_days",      180);
pref("browser.formfill.saveHttpsForms",   true);
pref("browser.formfill.agedWeight",       2);
pref("browser.formfill.bucketSize",       1);
pref("browser.formfill.maxTimeGroupings", 25);
pref("browser.formfill.timeGroupingSize", 604800);
pref("browser.formfill.boundaryWeight",   25);
pref("browser.formfill.prefixWeight",     5);

// Zoom prefs
pref("browser.zoom.full", false);
pref("zoom.minPercent", 30);
pref("zoom.maxPercent", 300);
pref("toolkit.zoomManager.zoomValues", ".3,.5,.67,.8,.9,1,1.1,1.2,1.33,1.5,1.7,2,2.4,3");

/**
 * Specify whether or not the browser should generate a reflow event on zoom.
 * For a pan-and-zoom ui on mobile, it is sometimes desirable for a zoom event
 * to limit the max line box width of text in order to enable easier reading
 * of large amounts of text.
 *
 * If enabled, this will limit the max line box width of all text on a page to
 * the viewport width (also generating a reflow), after a zoom event occurs.
 *
 * By default, this is not enabled.
 */
pref("browser.zoom.reflowOnZoom", false);

/**
 * Specifies the number of milliseconds to wait after a given reflow-on-zoom
 * operation has completed before allowing another one to be triggered. This
 * is to prevent a buildup of reflow-zoom events.
 */
pref("browser.zoom.reflowZoom.reflowTimeout", 500);

/**
 * Controls whether or not the reflow-on-zoom behavior happens on page load.
 * This can be enabled in conjunction with the above preference (reflowOnZoom),
 * but has no effect if browser.zoom.reflowOnZoom is disabled.
 *
 * Note that this should be turned off only in cases where debugging of the
 * reflow-on-zoom feature is necessary, and enabling the feature during
 * a page load inhbits this debugging.
 */
pref("browser.zoom.reflowZoom.reflowTextOnPageLoad", true);

// Image-related prefs
// The maximum size, in bytes, of the decoded images we cache
pref("image.cache.size", 5242880);
// A weight, from 0-1000, to place on time when comparing to size.
// Size is given a weight of 1000 - timeweight.
pref("image.cache.timeweight", 500);

// The default Accept header sent for images loaded over HTTP(S)
pref("image.http.accept", "image/png,image/*;q=0.8,*/*;q=0.5");

// Whether we do high-quality image downscaling. OS X natively supports
// high-quality image scaling.
//@line 3913 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("image.high_quality_downscaling.enabled", true);
//@line 3915 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// The minimum percent downscaling we'll use high-quality downscaling on,
// interpreted as a floating-point number / 1000.
pref("image.high_quality_downscaling.min_factor", 1000);

// The maximum memory size which we'll use high-quality uspcaling on,
// interpreted as number of decoded bytes.
pref("image.high_quality_upscaling.max_size", 20971520);

//
// Image memory management prefs
//

// Discards inactive image frames and re-decodes them on demand from
// compressed data.
pref("image.mem.discardable", true);

// Prevents images from automatically being decoded on load, instead allowing
// them to be decoded on demand when they are drawn.
pref("image.mem.decodeondraw", true);

// Minimum timeout for image discarding (in milliseconds). The actual time in
// which an image must inactive for it to be discarded will vary between this
// value and twice this value.
//
// This used to be 120 seconds, but having it that high causes our working
// set to grow very large. Switching it back to 10 seconds will hopefully
// be better.
pref("image.mem.min_discard_timeout_ms", 10000);

// Chunk size for calls to the image decoders
pref("image.mem.decode_bytes_at_a_time", 16384);

// The longest time we can spend in an iteration of an async decode
pref("image.mem.max_ms_before_yield", 5);

// The maximum amount of decoded image data we'll willingly keep around (we
// might keep around more than this, but we'll try to get down to this value).
pref("image.mem.max_decoded_image_kb", 51200);

// Whether we decode images on multiple background threads rather than the
// foreground thread.
pref("image.multithreaded_decoding.enabled", true);

// How many threads we'll use for multithreaded decoding. If < 0, will be
// automatically determined based on the system's number of cores.
pref("image.multithreaded_decoding.limit", -1);

// Limit for the canvas image cache. 0 means we don't limit the size of the
// cache.
pref("canvas.image.cache.limit", 0);

// How many images to eagerly decode on a given page. 0 means "no limit".
pref("image.onload.decode.limit", 0);

// WebGL prefs
pref("gl.msaa-level", 2);
pref("webgl.force-enabled", false);
pref("webgl.disabled", false);
pref("webgl.shader_validator", true);
pref("webgl.prefer-native-gl", false);
pref("webgl.min_capability_mode", false);
pref("webgl.disable-extensions", false);
pref("webgl.msaa-force", false);
pref("webgl.prefer-16bpp", false);
pref("webgl.default-no-alpha", false);
pref("webgl.force-layers-readback", false);
pref("webgl.lose-context-on-heap-minimize", false);
pref("webgl.can-lose-context-in-foreground", true);
pref("webgl.max-warnings-per-context", 32);
pref("webgl.enable-draft-extensions", false);
//@line 3989 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"


// Stagefright prefs
pref("stagefright.force-enabled", false);
pref("stagefright.disabled", false);

//@line 3999 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Asynchonous video compositing using the ImageBridge IPDL protocol.
// requires off-main-thread compositing.
pref("layers.async-video.enabled",false);

// Whether to disable acceleration for all widgets.
pref("layers.acceleration.disabled", false);

// Whether to force acceleration on, ignoring blacklists.
//@line 4013 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("layers.acceleration.force-enabled", false);
//@line 4015 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

pref("layers.acceleration.draw-fps", false);

pref("layers.draw-borders", false);

//@line 4023 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("layers.offmainthreadcomposition.enabled", false);
//@line 4025 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
// same effect as layers.offmainthreadcomposition.enabled, but specifically for
// use with tests.
pref("layers.offmainthreadcomposition.testing.enabled", false);
// Whether to animate simple opacity and transforms on the compositor
pref("layers.offmainthreadcomposition.async-animations", false);

//@line 4033 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("gfx.xrender.enabled",true);
//@line 4036 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 4048 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// Force all possible layers to be always active layers
pref("layers.force-active", false);

// Enable/Disable the geolocation API for content
pref("geo.enabled", true);

// Enable/Disable the orientation API for content
pref("device.sensors.enabled", true);

// Enable/Disable the device storage API for content
pref("device.storage.enabled", false);

// Toggle which thread the HTML5 parser uses for stream parsing
pref("html5.offmainthread", true);
// Time in milliseconds between the time a network buffer is seen and the 
// timer firing when the timer hasn't fired previously in this parse in the 
// off-the-main-thread HTML5 parser.
pref("html5.flushtimer.initialdelay", 120);
// Time in milliseconds between the time a network buffer is seen and the 
// timer firing when the timer has already fired previously in this parse.
pref("html5.flushtimer.subsequentdelay", 120);

// Push/Pop/Replace State prefs
pref("browser.history.allowPushState", true);
pref("browser.history.allowReplaceState", true);
pref("browser.history.allowPopState", true);
pref("browser.history.maxStateObjectSize", 655360);

// XPInstall prefs
pref("xpinstall.whitelist.required", true);
pref("extensions.alwaysUnpack", false);
pref("extensions.minCompatiblePlatformVersion", "2.0");

pref("network.buffer.cache.count", 24);
pref("network.buffer.cache.size",  32768);

// Desktop Notification
pref("notification.feature.enabled", false);

// Web Notification
pref("dom.webnotifications.enabled", true);

// Alert animation effect, name is disableSlidingEffect for backwards-compat.
pref("alerts.disableSlidingEffect", false);

// DOM full-screen API.
pref("full-screen-api.enabled", false);
pref("full-screen-api.allow-trusted-requests-only", true);
pref("full-screen-api.content-only", false);
pref("full-screen-api.pointer-lock.enabled", true);

// DOM idle observers API
pref("dom.idle-observers-api.enabled", true);

// Time limit, in milliseconds, for nsEventStateManager::IsHandlingUserInput().
// Used to detect long running handlers of user-generated events.
pref("dom.event.handling-user-input-time-limit", 1000);

// Whether we should layerize all animated images (if otherwise possible).
pref("layout.animated-image-layers.enabled", false);

pref("dom.vibrator.enabled", true);
pref("dom.vibrator.max_vibrate_ms", 10000);
pref("dom.vibrator.max_vibrate_list_len", 128);

// Battery API
pref("dom.battery.enabled", true);

// WebSMS
pref("dom.sms.enabled", false);
// Enable Latin characters replacement with corresponding ones in GSM SMS
// 7-bit default alphabet.
pref("dom.sms.strict7BitEncoding", false);
pref("dom.sms.requestStatusReport", true);

// WebContacts
pref("dom.mozContacts.enabled", false);
pref("dom.navigator-property.disable.mozContacts", true);
pref("dom.global-constructor.disable.mozContact", true);

// WebAlarms
pref("dom.mozAlarms.enabled", false);

// SimplePush
pref("services.push.enabled", false);

// WebNetworkStats
pref("dom.mozNetworkStats.enabled", false);

// WebSettings
pref("dom.mozSettings.enabled", false);
pref("dom.navigator-property.disable.mozSettings", true);
pref("dom.mozPermissionSettings.enabled", false);

// W3C touch events
// 0 - disabled, 1 - enabled, 2 - autodetect (win)
//@line 4148 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// enable JS dump() function.
pref("browser.dom.window.dump.enabled", false);

// SPS Profiler
pref("profiler.enabled", false);
pref("profiler.interval", 10);
pref("profiler.entries", 100000);

// Network API
pref("dom.network.enabled", true);
pref("dom.network.metered", false);

//@line 4179 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

// How long must we wait before declaring that a window is a "ghost" (i.e., a
// likely leak)?  This should be longer than it usually takes for an eligible
// window to be collected via the GC/CC.
pref("memory.ghost_window_timeout_seconds", 60);

// Disable freeing dirty pages when minimizing memory.
pref("memory.free_dirty_pages", false);

pref("social.enabled", false);
// comma separated list of domain origins (e.g. https://domain.com) for
// providers that can install from their own website without user warnings.
// entries are
pref("social.whitelist", "https://mozsocial.cliqz.com,https://now.msn.com,https://mixi.jp");
// omma separated list of domain origins (e.g. https://domain.com) for directory
// websites (e.g. AMO) that can install providers for other sites
pref("social.directories", "https://addons.mozilla.org");
// remote-install allows any website to activate a provider, with extended UI
// notifying user of installation. we can later pref off remote install if
// necessary. This does not affect whitelisted and directory installs.
pref("social.remote-install.enabled", true);
pref("social.toast-notifications.enabled", true);

// Disable idle observer fuzz, because only privileged content can access idle
// observers (bug 780507).
pref("dom.idle-observers-api.fuzz_time.disabled", true);

// Lowest localId for apps.
pref("dom.mozApps.maxLocalId", 1000);

// XXX Security: You CANNOT safely add a new app store for
// installing privileged apps just by modifying this pref and
// adding the signing cert for that store to the cert trust
// database. *Any* origin listed can install apps signed with
// *any* certificate trusted; we don't try to maintain a strong
// association between certificate with installOrign. The
// expectation here is that in production builds the pref will
// contain exactly one origin. However, in custom development
// builds it may contain more than one origin so we can test
// different stages (dev, staging, prod) of the same app store.
pref("dom.mozApps.signed_apps_installable_from", "https://marketplace.firefox.com");

// Minimum delay in milliseconds between network activity notifications (0 means
// no notifications). The delay is the same for both download and upload, though
// they are handled separately. This pref is only read once at startup:
// a restart is required to enable a new value.
pref("network.activity.blipIntervalMilliseconds", 0);

// If true, reuse the same global for everything loaded by the component loader
// (JS components, JSMs, etc).  This saves memory, but makes it possible for
// the scripts to interfere with each other.  A restart is required for this
// to take effect.
pref("jsloader.reuseGlobal", false);

// When we're asked to take a screenshot, don't wait more than 2000ms for the
// event loop to become idle before actually taking the screenshot.
pref("dom.browserElement.maxScreenshotDelayMS", 2000);

// Whether we should show the placeholder when the element is focused but empty.
pref("dom.placeholder.show_on_focus", true);

// UAProfile settings
pref("wap.UAProf.url", "");
pref("wap.UAProf.tagname", "x-wap-profile");

// Retrieval mode for MMS
// manual: Manual retrieval mode.
// automatic: Automatic retrieval mode even in roaming.
// automatic-home: Automatic retrieval mode in home network.
// never: Never retrieval mode.
pref("dom.mms.retrieval_mode", "manual");

pref("dom.mms.sendRetryCount", 3);
pref("dom.mms.sendRetryInterval", 300000);

pref("dom.mms.retrievalRetryCount", 4);
pref("dom.mms.retrievalRetryIntervals", "60000,300000,600000,1800000");

// Debug enabler for MMS.
pref("mms.debugging.enabled", false);

// If the user puts a finger down on an element and we think the user
// might be executing a pan gesture, how long do we wait before
// tentatively deciding the gesture is actually a tap and activating
// the target element?
pref("ui.touch_activation.delay_ms", 100);

// nsMemoryInfoDumper can watch a fifo in the temp directory and take various
// actions when the fifo is written to.  Disable this in general.
pref("memory_info_dumper.watch_fifo", false);

//@line 4275 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"

//@line 4277 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/modules/libpref/src/init/all.js"
pref("dom.forms.inputmode", false);
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

pref("datareporting.policy.dataSubmissionEnabled", true);
pref("datareporting.policy.dataSubmissionPolicyAccepted", false);
pref("datareporting.policy.dataSubmissionPolicyBypassAcceptance", false);
pref("datareporting.policy.dataSubmissionPolicyNotifiedTime", "0");
pref("datareporting.policy.dataSubmissionPolicyResponseType", "");
pref("datareporting.policy.dataSubmissionPolicyResponseTime", "0");
pref("datareporting.policy.firstRunTime", "0");

